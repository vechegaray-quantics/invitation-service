from datetime import UTC, datetime
from html import escape
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, status

from app.core.config import settings
from app.db import SessionLocal
from app.models.invitation import Invitation
from app.models.invitation_batch import InvitationBatch
from app.repositories.audience_repository import AudienceRepository
from app.repositories.invitation_batch_repository import InvitationBatchRepository
from app.repositories.invitation_repository import InvitationRepository
from app.schemas.invitation_batch import InvitationBatchCreateRequest
from app.services.email_sender import EmailToSend, email_sender


class InvitationBatchService:
    def __init__(self) -> None:
        self._batch_repository = InvitationBatchRepository()
        self._audience_repository = AudienceRepository()
        self._invitation_repository = InvitationRepository()
        self._template_cache: str | None = None

    def create_batch(
        self,
        tenant_id: str,
        payload: InvitationBatchCreateRequest,
    ) -> dict:
        with SessionLocal() as session:
            audience_items = self._audience_repository.list_for_campaign(
                session=session,
                tenant_id=tenant_id,
                campaign_id=payload.campaignId,
            )

            recipient_count = len(audience_items)

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
                campaign_name=payload.campaignName,
                email_subject=payload.emailSubject,
                email_message=payload.emailMessage,
                sender_email=payload.senderEmail,
                recipient_count=recipient_count,
                sent_count=0,
                failed_count=0,
                created_at=now,
                updated_at=now,
            )

            created = self._batch_repository.create(session, batch)

            invitations = []
            for item in audience_items:
                invite_token = f"tok_{uuid4().hex}"
                invite_url = f"{settings.public_interview_base_url.rstrip('/')}/{invite_token}"

                invitations.append(
                    Invitation(
                        invitation_id=f"inv_{uuid4().hex[:12]}",
                        tenant_id=tenant_id,
                        batch_id=created.batch_id,
                        campaign_id=payload.campaignId,
                        recipient_email=item.email,
                        status="draft",
                        invite_token=invite_token,
                        invite_url=invite_url,
                        provider_message_id=None,
                        last_error=None,
                        created_at=now,
                        updated_at=now,
                        sent_at=None,
                    )
                )

            self._invitation_repository.create_many(session, invitations)
            session.refresh(created)
            response = self._to_response(created)

        return response

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

            response = self._to_response(batch)

        return response

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

            invitations = self._invitation_repository.list_by_batch(
                session=session,
                tenant_id=tenant_id,
                batch_id=batch_id,
            )

            pending = [item for item in invitations if item.status == "draft"]

            if pending:
                now = datetime.now(UTC).replace(tzinfo=None)

                payloads = [
                    EmailToSend(
                        to_email=invitation.recipient_email,
                        subject=batch.email_subject,
                        html=self._render_invitation_html(batch, invitation),
                    )
                    for invitation in pending
                ]

                results = []
                for chunk in self._chunked(payloads, 100):
                    results.extend(email_sender.send_batch(chunk))

                for invitation, result in zip(pending, results, strict=True):
                    if result.success:
                        invitation.status = "sent"
                        invitation.provider_message_id = result.provider_message_id
                        invitation.last_error = None
                        invitation.sent_at = now
                    else:
                        invitation.status = "failed"
                        invitation.provider_message_id = None
                        invitation.last_error = result.error
                        invitation.sent_at = None

                    invitation.updated_at = now
                    session.add(invitation)

                session.commit()

            refreshed = self._invitation_repository.list_by_batch(
                session=session,
                tenant_id=tenant_id,
                batch_id=batch_id,
            )

            batch.sent_count = sum(1 for item in refreshed if item.status == "sent")
            batch.failed_count = sum(1 for item in refreshed if item.status == "failed")
            batch.status = "completed"
            batch.updated_at = datetime.now(UTC).replace(tzinfo=None)

            session.add(batch)
            session.commit()
            session.refresh(batch)

            response = self._to_response(batch)

        return response

    def list_invitations_by_batch(
        self,
        tenant_id: str,
        batch_id: str,
    ) -> list[dict]:
        with SessionLocal() as session:
            invitations = self._invitation_repository.list_by_batch(
                session=session,
                tenant_id=tenant_id,
                batch_id=batch_id,
            )
            items = [self._invitation_to_response(item) for item in invitations]

        return items

    def list_invitations_by_campaign(
        self,
        tenant_id: str,
        campaign_id: str,
    ) -> list[dict]:
        with SessionLocal() as session:
            invitations = self._invitation_repository.list_by_campaign(
                session=session,
                tenant_id=tenant_id,
                campaign_id=campaign_id,
            )
            items = [self._invitation_to_response(item) for item in invitations]

        return items

    @staticmethod
    def _chunked(items: list[EmailToSend], size: int) -> list[list[EmailToSend]]:
        return [items[index:index + size] for index in range(0, len(items), size)]

    @staticmethod
    def _guess_name_from_email(email: str) -> str:
        local_part = email.split("@", 1)[0]
        name = local_part.replace(".", " ").replace("_", " ").replace("-", " ").strip()
        return name.title() if name else email

    def _load_email_template(self) -> str:
        if self._template_cache is not None:
            return self._template_cache

        template_path = Path(__file__).resolve().parents[1] / "templates" / "invitation_email.html"
        self._template_cache = template_path.read_text(encoding="utf-8")
        return self._template_cache

    def _render_invitation_html(
        self,
        batch: InvitationBatch,
        invitation: Invitation,
    ) -> str:
        template = self._load_email_template()

        guessed_name = self._guess_name_from_email(invitation.recipient_email)

        rendered_message = (
            batch.email_message
            .replace("{{nombre}}", guessed_name)
            .replace("{{email}}", invitation.recipient_email)
            .replace("{{campaign_name}}", batch.campaign_name)
        )

        email_message_html = "<p style=\"margin:0 0 16px;\">{}</p>".format(
            "</p><p style=\"margin:0 0 16px;\">".join(
                escape(line) for line in rendered_message.splitlines() if line.strip()
            )
        )

        if email_message_html == '<p style="margin:0 0 16px;"></p>':
            email_message_html = "<p style=\"margin:0 0 16px;\">Te invitamos a participar en esta campaña.</p>"

        replacements = {
            "{{logo_url}}": settings.email_logo_url,
            "{{hero_image_url}}": settings.email_hero_image_url,
            "{{email_subject}}": escape(batch.email_subject),
            "{{nombre}}": escape(guessed_name),
            "{{campaign_name}}": escape(batch.campaign_name),
            "{{cta_link}}": escape(invitation.invite_url),
            "{{support_email}}": escape(settings.email_support_email),
            "{{email_message_html}}": email_message_html,
        }

        html = template
        for placeholder, value in replacements.items():
            html = html.replace(placeholder, value)

        return html

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

    @staticmethod
    def _invitation_to_response(invitation: Invitation) -> dict:
        return {
            "invitationId": invitation.invitation_id,
            "batchId": invitation.batch_id,
            "campaignId": invitation.campaign_id,
            "recipientEmail": invitation.recipient_email,
            "status": invitation.status,
            "inviteToken": invitation.invite_token,
            "inviteUrl": invitation.invite_url,
            "providerMessageId": invitation.provider_message_id,
            "lastError": invitation.last_error,
            "createdAt": invitation.created_at,
            "updatedAt": invitation.updated_at,
            "sentAt": invitation.sent_at,
        }


invitation_batch_service = InvitationBatchService()