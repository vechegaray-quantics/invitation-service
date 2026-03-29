from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.invitation import Invitation


class InvitationRepository:
    def create_many(
        self,
        session: Session,
        invitations: list[Invitation],
    ) -> list[Invitation]:
        session.add_all(invitations)
        session.commit()
        return invitations

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
            .order_by(Invitation.created_at.asc(), Invitation.recipient_email.asc())
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
            .order_by(Invitation.created_at.asc(), Invitation.recipient_email.asc())
        )
        return list(session.execute(stmt).scalars().all())

    def mark_batch_sent(
        self,
        session: Session,
        tenant_id: str,
        batch_id: str,
        sent_at: datetime,
    ) -> list[Invitation]:
        invitations = self.list_by_batch(session, tenant_id, batch_id)

        for invitation in invitations:
            invitation.status = "sent"
            invitation.sent_at = sent_at
            invitation.updated_at = sent_at
            session.add(invitation)

        session.commit()
        return invitations