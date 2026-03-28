from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.audience_participant import AudienceParticipant


class AudienceRepository:
    def replace_for_campaign(
        self,
        session: Session,
        tenant_id: str,
        campaign_id: str,
        items: list[AudienceParticipant],
    ) -> list[AudienceParticipant]:
        session.execute(
            delete(AudienceParticipant).where(
                AudienceParticipant.tenant_id == tenant_id,
                AudienceParticipant.campaign_id == campaign_id,
            )
        )

        session.add_all(items)
        session.commit()

        return items

    def list_for_campaign(
        self,
        session: Session,
        tenant_id: str,
        campaign_id: str,
    ) -> list[AudienceParticipant]:
        stmt = (
            select(AudienceParticipant)
            .where(
                AudienceParticipant.tenant_id == tenant_id,
                AudienceParticipant.campaign_id == campaign_id,
            )
            .order_by(AudienceParticipant.created_at.asc(), AudienceParticipant.email.asc())
        )

        return list(session.execute(stmt).scalars().all())