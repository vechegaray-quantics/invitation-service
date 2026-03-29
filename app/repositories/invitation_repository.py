from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.invitation import Invitation


class InvitationRepository:
    def create_many(
        self,
        session: Session,
        invitations: list[Invitation],
    ) -> None:
        session.add_all(invitations)
        session.commit()

    def list_by_batch(
        self,
        session: Session,
        tenant_id: str,
        batch_id: str,
    ) -> list[Invitation]:
        stmt = (
            select(Invitation)
            .where(
                Invitation.tenant_id == tenant_id,
                Invitation.batch_id == batch_id,
            )
            .order_by(Invitation.created_at.asc())
        )
        return list(session.execute(stmt).scalars().all())

    def list_by_campaign(
        self,
        session: Session,
        tenant_id: str,
        campaign_id: str,
    ) -> list[Invitation]:
        stmt = (
            select(Invitation)
            .where(
                Invitation.tenant_id == tenant_id,
                Invitation.campaign_id == campaign_id,
            )
            .order_by(Invitation.created_at.asc())
        )
        return list(session.execute(stmt).scalars().all())

    def get_by_token(
        self,
        session: Session,
        invite_token: str,
    ) -> Invitation | None:
        stmt = select(Invitation).where(Invitation.invite_token == invite_token)
        return session.execute(stmt).scalar_one_or_none()