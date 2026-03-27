from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def tenant_headers(tenant_id: str) -> dict[str, str]:
    return {
        "X-Tenant-Id": tenant_id,
    }


def test_upsert_campaign_audience_requires_tenant_header() -> None:
    payload = {
        "participants": [
            {"email": "ana@empresa.com"},
        ]
    }

    response = client.put("/v1/campaign-audiences/camp_123", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "X-Tenant-Id header is required"


def test_upsert_campaign_audience_counts_valid_invalid_and_duplicates() -> None:
    payload = {
        "participants": [
            {"email": "ana@empresa.com"},
            {"email": "juan@empresa.com"},
            {"email": "ana@empresa.com"},
            {"email": "correo-invalido"},
        ]
    }

    response = client.put(
        "/v1/campaign-audiences/camp_123",
        json=payload,
        headers=tenant_headers("tenant-dev"),
    )

    assert response.status_code == 200
    assert response.json() == {
        "campaignId": "camp_123",
        "totalReceived": 4,
        "totalAccepted": 2,
        "totalInvalid": 1,
        "totalDuplicates": 1,
    }


def test_get_campaign_audience_returns_saved_items_for_same_tenant() -> None:
    payload = {
        "participants": [
            {"email": "ana@empresa.com"},
            {"email": "juan@empresa.com"},
        ]
    }

    save_response = client.put(
        "/v1/campaign-audiences/camp_abc",
        json=payload,
        headers=tenant_headers("tenant-dev"),
    )
    assert save_response.status_code == 200

    response = client.get(
        "/v1/campaign-audiences/camp_abc",
        headers=tenant_headers("tenant-dev"),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["campaignId"] == "camp_abc"
    assert len(body["items"]) == 2
    assert body["items"][0]["participantId"].startswith("part_")
    assert body["items"][0]["status"] == "active"


def test_get_campaign_audience_is_isolated_by_tenant() -> None:
    payload = {
        "participants": [
            {"email": "ana@empresa.com"},
        ]
    }

    save_response = client.put(
        "/v1/campaign-audiences/camp_xyz",
        json=payload,
        headers=tenant_headers("tenant-dev"),
    )
    assert save_response.status_code == 200

    response = client.get(
        "/v1/campaign-audiences/camp_xyz",
        headers=tenant_headers("tenant-otro"),
    )

    assert response.status_code == 200
    assert response.json() == {
        "campaignId": "camp_xyz",
        "items": [],
    }