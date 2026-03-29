from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Invitation(Base):
    __tablename__ = "invitations"

    invitation_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    batch_id: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    campaign_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)

    recipient_email: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)

    invite_token: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    invite_url: Mapped[str] = mapped_column(String(500), nullable=False)

    provider_message_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)