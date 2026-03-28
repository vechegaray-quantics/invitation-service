from datetime import datetime

from pydantic import BaseModel, Field


class InvitationBatchCreateRequest(BaseModel):
    campaignId: str = Field(min_length=3)


class InvitationBatchResponse(BaseModel):
    batchId: str
    campaignId: str
    status: str
    recipientCount: int
    sentCount: int
    failedCount: int
    createdAt: datetime
    updatedAt: datetime