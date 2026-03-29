from fastapi import APIRouter, Header, HTTPException, status

from app.core.config import settings
from app.db import SessionLocal
from app.repositories.invitation_repository import InvitationRepository


router = APIRouter(prefix="/internal/v1/invitations", tags=["internal-invitations"])

_repository = InvitationRepository()


@router.get("/by-token/{invite_token}")
def get_invitation_by_token(
    invite_token: str,
    x_internal_service_token: str = Header(default="", alias="X-Internal-Service-Token"),
) -> dict:
    if x_internal_service_token != settings.internal_service_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid internal service token",
        )

    with SessionLocal() as session:
        invitation = _repository.get_by_token(session=session, invite_token=invite_token)

        if invitation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found",
            )

        return {
            "invitationId": invitation.invitation_id,
            "campaignId": invitation.campaign_id,
            "tenantId": invitation.tenant_id,
            "recipientEmail": invitation.recipient_email,
            "status": invitation.status,
            "inviteToken": invitation.invite_token,
        }