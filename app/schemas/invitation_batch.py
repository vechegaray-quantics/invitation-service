from datetime import datetime

from pydantic import BaseModel, Field


class InvitationBatchCreateRequest(BaseModel):
    campaignId: str = Field(min_length=3)
    campaignName: str = Field(min_length=3)
    emailSubject: str = Field(min_length=1)
    emailMessage: str = Field(min_length=1)
    senderEmail: str = Field(min_length=3)


class InvitationBatchResponse(BaseModel):
    batchId: str
    campaignId: str
    status: str
    recipientCount: int
    sentCount: int
    failedCount: int
    createdAt: datetime
    updatedAt: datetime