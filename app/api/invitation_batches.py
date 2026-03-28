from fastapi import APIRouter, Depends

from app.dependencies.auth import get_tenant_id
from app.schemas.invitation_batch import (
    InvitationBatchCreateRequest,
    InvitationBatchResponse,
)
from app.services.invitation_batch_service import invitation_batch_service


router = APIRouter(prefix="/v1/invitation-batches", tags=["invitation-batches"])


@router.post("", response_model=InvitationBatchResponse)
def create_invitation_batch(
    payload: InvitationBatchCreateRequest,
    tenant_id: str = Depends(get_tenant_id),
) -> InvitationBatchResponse:
    result = invitation_batch_service.create_batch(tenant_id, payload)
    return InvitationBatchResponse(**result)


@router.get("/{batch_id}", response_model=InvitationBatchResponse)
def get_invitation_batch(
    batch_id: str,
    tenant_id: str = Depends(get_tenant_id),
) -> InvitationBatchResponse:
    result = invitation_batch_service.get_batch(tenant_id, batch_id)
    return InvitationBatchResponse(**result)


@router.post("/{batch_id}/send", response_model=InvitationBatchResponse)
def send_invitation_batch(
    batch_id: str,
    tenant_id: str = Depends(get_tenant_id),
) -> InvitationBatchResponse:
    result = invitation_batch_service.send_batch(tenant_id, batch_id)
    return InvitationBatchResponse(**result)