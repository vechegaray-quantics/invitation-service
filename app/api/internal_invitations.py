from datetime import UTC, datetime

from fastapi import APIRouter, Header, HTTPException, status

from app.core.config import settings
from app.db import SessionLocal
from app.repositories.invitation_repository import InvitationRepository


router = APIRouter(prefix="/internal/v1/invitations", tags=["internal-invitations"])

_repository = InvitationRepository()


def _validate_internal_token(x_internal_service_token: str) -> None:
    if x_internal_service_token != settings.internal_service_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid internal service token",
        )


@router.get("/by-token/{invite_token}")
def get_invitation_by_token(
    invite_token: str,
    x_internal_service_token: str = Header(default="", alias="X-Internal-Service-Token"),
) -> dict:
    _validate_internal_token(x_internal_service_token)

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


@router.post("/{invitation_id}/complete")
def mark_invitation_completed(
    invitation_id: str,
    x_internal_service_token: str = Header(default="", alias="X-Internal-Service-Token"),
) -> dict:
    _validate_internal_token(x_internal_service_token)

    with SessionLocal() as session:
        invitation = _repository.get_by_id(session=session, invitation_id=invitation_id)

        if invitation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found",
            )

        if invitation.status != "completed":
            invitation.status = "completed"
            invitation.updated_at = datetime.now(UTC).replace(tzinfo=None)
            session.add(invitation)
            session.commit()
            session.refresh(invitation)

        return {
            "invitationId": invitation.invitation_id,
            "status": invitation.status,
        }