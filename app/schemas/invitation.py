from datetime import datetime

from pydantic import BaseModel


class InvitationResponse(BaseModel):
    invitationId: str
    batchId: str
    campaignId: str
    recipientEmail: str
    status: str
    inviteToken: str
    inviteUrl: str
    providerMessageId: str | None = None
    lastError: str | None = None
    createdAt: datetime
    updatedAt: datetime
    sentAt: datetime | None = None


class InvitationListResponse(BaseModel):
    items: list[InvitationResponse]