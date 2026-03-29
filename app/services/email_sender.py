from dataclasses import dataclass

import httpx

from app.core.config import settings


@dataclass
class EmailToSend:
    to_email: str
    subject: str
    html: str


@dataclass
class EmailSendResult:
    success: bool
    provider_message_id: str | None = None
    error: str | None = None


class ResendEmailSender:
    def __init__(self) -> None:
        self._api_url = "https://api.resend.com/emails/batch"

    def send_batch(self, emails: list[EmailToSend]) -> list[EmailSendResult]:
        if not emails:
            return []

        if not settings.resend_api_key:
            return [
                EmailSendResult(
                    success=False,
                    error="RESEND_API_KEY is not configured",
                )
                for _ in emails
            ]

        payload = [
            {
                "from": settings.email_from,
                "to": [email.to_email],
                "subject": email.subject,
                "html": email.html,
            }
            for email in emails
        ]

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    self._api_url,
                    headers={
                        "Authorization": f"Bearer {settings.resend_api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
                data = response.json().get("data", [])
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text or str(exc)
            return [
                EmailSendResult(
                    success=False,
                    error=f"Resend HTTP {exc.response.status_code}: {detail}",
                )
                for _ in emails
            ]
        except httpx.HTTPError as exc:
            return [
                EmailSendResult(
                    success=False,
                    error=f"Resend request failed: {exc}",
                )
                for _ in emails
            ]

        results: list[EmailSendResult] = []

        for index, _ in enumerate(emails):
            item = data[index] if index < len(data) and isinstance(data[index], dict) else {}
            provider_message_id = item.get("id")

            if provider_message_id:
                results.append(
                    EmailSendResult(
                        success=True,
                        provider_message_id=provider_message_id,
                    )
                )
            else:
                results.append(
                    EmailSendResult(
                        success=False,
                        error="Resend did not return a message id",
                    )
                )

        return results


email_sender = ResendEmailSender()