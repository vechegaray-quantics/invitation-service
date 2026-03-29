from fastapi.testclient import TestClient

from app.main import app
from app.services.email_sender import EmailSendResult
from app.services.invitation_batch_service import email_sender


client = TestClient(app)


def tenant_headers(tenant_id: str) -> dict[str, str]:
    return {"X-Tenant-Id": tenant_id}


def create_audience(campaign_id: str, emails: list[str], tenant_id: str = "tenant-dev") -> None:
    response = client.put(
        f"/v1/campaign-audiences/{campaign_id}",
        json={"participants": [{"email": email} for email in emails]},
        headers=tenant_headers(tenant_id),
    )
    assert response.status_code == 200


def batch_payload(campaign_id: str) -> dict:
    return {
        "campaignId": campaign_id,
        "campaignName": "Campaña MVP",
        "emailSubject": "Queremos conocer tu opinión",
        "emailMessage": "Hola {{nombre}}, participa en {{campaign_name}}.",
        "senderEmail": "research@empresa.com",
    }


def create_batch(campaign_id: str, tenant_id: str = "tenant-dev") -> str:
    response = client.post(
        "/v1/invitation-batches",
        json=batch_payload(campaign_id),
        headers=tenant_headers(tenant_id),
    )
    assert response.status_code == 200
    return response.json()["batchId"]


def test_list_invitations_by_batch_returns_created_invitations() -> None:
    create_audience("camp_inv_1", ["ana@empresa.com", "juan@empresa.com"])
    batch_id = create_batch("camp_inv_1")

    response = client.get(
        f"/v1/invitations?batchId={batch_id}",
        headers=tenant_headers("tenant-dev"),
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 2
    assert body["items"][0]["invitationId"].startswith("inv_")
    assert body["items"][0]["batchId"] == batch_id
    assert body["items"][0]["status"] == "draft"
    assert body["items"][0]["inviteToken"].startswith("tok_")
    assert body["items"][0]["providerMessageId"] is None
    assert body["items"][0]["lastError"] is None
    assert "/interview/" in body["items"][0]["inviteUrl"]


def test_send_batch_marks_invitations_as_sent(monkeypatch) -> None:
    create_audience("camp_inv_2", ["ana@empresa.com", "juan@empresa.com"])
    batch_id = create_batch("camp_inv_2")

    def fake_send_batch(emails):
        return [
            EmailSendResult(success=True, provider_message_id=f"msg_{index}")
            for index, _ in enumerate(emails)
        ]

    monkeypatch.setattr(email_sender, "send_batch", fake_send_batch)

    send_response = client.post(
        f"/v1/invitation-batches/{batch_id}/send",
        headers=tenant_headers("tenant-dev"),
    )
    assert send_response.status_code == 200

    response = client.get(
        f"/v1/invitations?batchId={batch_id}",
        headers=tenant_headers("tenant-dev"),
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 2
    assert all(item["status"] == "sent" for item in body["items"])
    assert all(item["sentAt"] is not None for item in body["items"])
    assert all(item["providerMessageId"] is not None for item in body["items"])
    assert all(item["lastError"] is None for item in body["items"])


def test_list_invitations_by_campaign_returns_all_campaign_invitations() -> None:
    create_audience("camp_inv_3", ["ana@empresa.com", "juan@empresa.com", "maria@empresa.com"])
    batch_id = create_batch("camp_inv_3")

    response = client.get(
        "/v1/invitations?campaignId=camp_inv_3",
        headers=tenant_headers("tenant-dev"),
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 3
    assert all(item["batchId"] == batch_id for item in body["items"])


def test_list_invitations_requires_batch_or_campaign_filter() -> None:
    response = client.get(
        "/v1/invitations",
        headers=tenant_headers("tenant-dev"),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Either batchId or campaignId is required"