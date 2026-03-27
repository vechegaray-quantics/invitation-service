from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from email_validator import EmailNotValidError, validate_email

from app.schemas.audience import CampaignAudienceUpsertRequest


class AudienceService:
    def __init__(self) -> None:
        self._store: dict[tuple[str, str], list[dict[str, Any]]] = {}

    def upsert_audience(
        self,
        tenant_id: str,
        campaign_id: str,
        payload: CampaignAudienceUpsertRequest,
    ) -> dict[str, Any]:
        seen: set[str] = set()
        accepted_emails: list[str] = []
        invalid_count = 0
        duplicate_count = 0

        for participant in payload.participants:
            raw_email = participant.email.strip().lower()

            try:
                normalized = validate_email(
                    raw_email,
                    check_deliverability=False,
                ).normalized
            except EmailNotValidError:
                invalid_count += 1
                continue

            if normalized in seen:
                duplicate_count += 1
                continue

            seen.add(normalized)
            accepted_emails.append(normalized)

        now = datetime.now(UTC).replace(tzinfo=None)
        items = [
            {
                "participantId": f"part_{uuid4().hex[:12]}",
                "email": email,
                "status": "active",
                "createdAt": now,
            }
            for email in accepted_emails
        ]

        self._store[(tenant_id, campaign_id)] = items

        return {
            "campaignId": campaign_id,
            "totalReceived": len(payload.participants),
            "totalAccepted": len(accepted_emails),
            "totalInvalid": invalid_count,
            "totalDuplicates": duplicate_count,
        }

    def get_audience(self, tenant_id: str, campaign_id: str) -> dict[str, Any]:
        items = self._store.get((tenant_id, campaign_id), [])

        return {
            "campaignId": campaign_id,
            "items": items,
        }


audience_service = AudienceService()
