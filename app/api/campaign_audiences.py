from fastapi import APIRouter, Depends

from app.dependencies.auth import get_tenant_id
from app.schemas.audience import (
    CampaignAudienceResponse,
    CampaignAudienceUpsertRequest,
    CampaignAudienceUpsertResponse,
)
from app.services.audience_service import audience_service


router = APIRouter(prefix="/v1/campaign-audiences", tags=["campaign-audiences"])


@router.put("/{campaign_id}", response_model=CampaignAudienceUpsertResponse)
def upsert_campaign_audience(
    campaign_id: str,
    payload: CampaignAudienceUpsertRequest,
    tenant_id: str = Depends(get_tenant_id),
) -> CampaignAudienceUpsertResponse:
    result = audience_service.upsert_audience(tenant_id, campaign_id, payload)
    return CampaignAudienceUpsertResponse(**result)


@router.get("/{campaign_id}", response_model=CampaignAudienceResponse)
def get_campaign_audience(
    campaign_id: str,
    tenant_id: str = Depends(get_tenant_id),
) -> CampaignAudienceResponse:
    result = audience_service.get_audience(tenant_id, campaign_id)
    return CampaignAudienceResponse(**result)