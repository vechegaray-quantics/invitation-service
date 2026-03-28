from datetime import UTC, datetime
from uuid import uuid4

from fastapi import HTTPException, status

from app.db import SessionLocal
from app.models.invitation_batch import InvitationBatch
from app.repositories.audience_repository import AudienceRepository
from app.repositories.invitation_batch_repository import InvitationBatchRepository
from app.schemas.invitation_batch import InvitationBatchCreateRequest


class InvitationBatchService:
    def __init__(self) -> None:
        self._batch_repository = InvitationBatchRepository()
        self._audience_repository = AudienceRepository()

    def create_batch(
        self,
        tenant_id: str,
        payload: InvitationBatchCreateRequest,
    ) -> dict:
        with SessionLocal() as session:
            recipient_count = self._audience_repository.count_for_campaign(
                session=session,
                tenant_id=tenant_id,
                campaign_id=payload.campaignId,
            )

            if recipient_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Campaign audience is empty",
                )

            now = datetime.now(UTC).replace(tzinfo=None)

            batch = InvitationBatch(
                batch_id=f"batch_{uuid4().hex[:12]}",
                tenant_id=tenant_id,
                campaign_id=payload.campaignId,
                status="draft",
                recipient_count=recipient_count,
                sent_count=0,
                failed_count=0,
                created_at=now,
                updated_at=now,
            )

            created = self._batch_repository.create(session, batch)

        return self._to_response(created)

    def get_batch(
        self,
        tenant_id: str,
        batch_id: str,
    ) -> dict:
        with SessionLocal() as session:
            batch = self._batch_repository.get_by_id(
                session=session,
                tenant_id=tenant_id,
                batch_id=batch_id,
            )

            if batch is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Invitation batch not found",
                )

        return self._to_response(batch)

    def send_batch(
        self,
        tenant_id: str,
        batch_id: str,
    ) -> dict:
        with SessionLocal() as session:
            batch = self._batch_repository.get_by_id(
                session=session,
                tenant_id=tenant_id,
                batch_id=batch_id,
            )

            if batch is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Invitation batch not found",
                )

            if batch.status != "completed":
                batch = self._batch_repository.mark_completed(
                    session=session,
                    batch=batch,
                    updated_at=datetime.now(UTC).replace(tzinfo=None),
                )

        return self._to_response(batch)

    @staticmethod
    def _to_response(batch: InvitationBatch) -> dict:
        return {
            "batchId": batch.batch_id,
            "campaignId": batch.campaign_id,
            "status": batch.status,
            "recipientCount": batch.recipient_count,
            "sentCount": batch.sent_count,
            "failedCount": batch.failed_count,
            "createdAt": batch.created_at,
            "updatedAt": batch.updated_at,
        }


invitation_batch_service = InvitationBatchService()