from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies.auth import get_tenant_id
from app.schemas.invitation import InvitationListResponse, InvitationResponse
from app.services.invitation_batch_service import invitation_batch_service


router = APIRouter(prefix="/v1/invitations", tags=["invitations"])


@router.get("", response_model=InvitationListResponse)
def list_invitations(
    batch_id: str | None = Query(default=None, alias="batchId"),
    campaign_id: str | None = Query(default=None, alias="campaignId"),
    tenant_id: str = Depends(get_tenant_id),
) -> InvitationListResponse:
    if not batch_id and not campaign_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either batchId or campaignId is required",
        )

    if batch_id and campaign_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use either batchId or campaignId, not both",
        )

    if batch_id:
        items = invitation_batch_service.list_invitations_by_batch(tenant_id, batch_id)
    else:
        items = invitation_batch_service.list_invitations_by_campaign(tenant_id, campaign_id)

    return InvitationListResponse(
        items=[InvitationResponse(**item) for item in items],
    )