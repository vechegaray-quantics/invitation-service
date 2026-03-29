from fastapi.testclient import TestClient

from app.main import app
from app.services.email_sender import EmailSendResult
from app.services.invitation_batch_service import email_sender


client = TestClient(app)


def tenant_headers(tenant_id: str) -> dict[str, str]:
    return {"X-Tenant-Id": tenant_id}


def create_audience(campaign_id: str, emails: list[str], tenant_id: str = "tenant-dev") -> None:
    payload = {
        "participants": [{"email": email} for email in emails]
    }
    response = client.put(
        f"/v1/campaign-audiences/{campaign_id}",
        json=payload,
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


def test_create_invitation_batch_fails_when_audience_is_empty() -> None:
    response = client.post(
        "/v1/invitation-batches",
        json=batch_payload("camp_empty"),
        headers=tenant_headers("tenant-dev"),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Campaign audience is empty"


def test_create_invitation_batch_returns_draft_batch() -> None:
    create_audience("camp_batch_1", ["ana@empresa.com", "juan@empresa.com"])

    response = client.post(
        "/v1/invitation-batches",
        json=batch_payload("camp_batch_1"),
        headers=tenant_headers("tenant-dev"),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["batchId"].startswith("batch_")
    assert body["campaignId"] == "camp_batch_1"
    assert body["status"] == "draft"
    assert body["recipientCount"] == 2
    assert body["sentCount"] == 0
    assert body["failedCount"] == 0


def test_get_invitation_batch_returns_existing_batch() -> None:
    create_audience("camp_batch_2", ["ana@empresa.com"])

    create_response = client.post(
        "/v1/invitation-batches",
        json=batch_payload("camp_batch_2"),
        headers=tenant_headers("tenant-dev"),
    )
    assert create_response.status_code == 200

    batch_id = create_response.json()["batchId"]

    response = client.get(
        f"/v1/invitation-batches/{batch_id}",
        headers=tenant_headers("tenant-dev"),
    )

    assert response.status_code == 200
    assert response.json()["batchId"] == batch_id
    assert response.json()["campaignId"] == "camp_batch_2"


def test_send_invitation_batch_marks_it_completed(monkeypatch) -> None:
    create_audience("camp_batch_3", ["ana@empresa.com", "juan@empresa.com", "maria@empresa.com"])

    create_response = client.post(
        "/v1/invitation-batches",
        json=batch_payload("camp_batch_3"),
        headers=tenant_headers("tenant-dev"),
    )
    assert create_response.status_code == 200

    batch_id = create_response.json()["batchId"]

    def fake_send_batch(emails):
        return [
            EmailSendResult(success=True, provider_message_id=f"msg_{index}")
            for index, _ in enumerate(emails)
        ]

    monkeypatch.setattr(email_sender, "send_batch", fake_send_batch)

    response = client.post(
        f"/v1/invitation-batches/{batch_id}/send",
        headers=tenant_headers("tenant-dev"),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["recipientCount"] == 3
    assert body["sentCount"] == 3
    assert body["failedCount"] == 0


def test_get_invitation_batch_is_isolated_by_tenant() -> None:
    create_audience("camp_batch_4", ["ana@empresa.com"], tenant_id="tenant-dev")

    create_response = client.post(
        "/v1/invitation-batches",
        json=batch_payload("camp_batch_4"),
        headers=tenant_headers("tenant-dev"),
    )
    assert create_response.status_code == 200

    batch_id = create_response.json()["batchId"]

    response = client.get(
        f"/v1/invitation-batches/{batch_id}",
        headers=tenant_headers("tenant-otro"),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Invitation batch not found"