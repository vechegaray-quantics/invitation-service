from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.invitation_batch import InvitationBatch


class InvitationBatchRepository:
    def create(
        self,
        session: Session,
        batch: InvitationBatch,
    ) -> InvitationBatch:
        session.add(batch)
        session.commit()
        session.refresh(batch)
        return batch

    def get_by_id(
        self,
        session: Session,
        tenant_id: str,
        batch_id: str,
    ) -> InvitationBatch | None:
        stmt = select(InvitationBatch).where(
            InvitationBatch.tenant_id == tenant_id,
            InvitationBatch.batch_id == batch_id,
        )
        return session.execute(stmt).scalar_one_or_none()

    def mark_completed(
        self,
        session: Session,
        batch: InvitationBatch,
        updated_at: datetime,
    ) -> InvitationBatch:
        batch.status = "completed"
        batch.sent_count = batch.recipient_count
        batch.failed_count = 0
        batch.updated_at = updated_at

        session.add(batch)
        session.commit()
        session.refresh(batch)
        return batch