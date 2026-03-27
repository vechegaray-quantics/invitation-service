from datetime import datetime

from pydantic import BaseModel, Field


class AudienceParticipantInput(BaseModel):
    email: str = Field(min_length=3)


class CampaignAudienceUpsertRequest(BaseModel):
    participants: list[AudienceParticipantInput]


class CampaignAudienceUpsertResponse(BaseModel):
    campaignId: str
    totalReceived: int
    totalAccepted: int
    totalInvalid: int
    totalDuplicates: int


class AudienceParticipantResponse(BaseModel):
    participantId: str
    email: str
    status: str
    createdAt: datetime


class CampaignAudienceResponse(BaseModel):
    campaignId: str
    items: list[AudienceParticipantResponse]