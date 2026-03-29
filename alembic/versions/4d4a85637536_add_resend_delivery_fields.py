"""add resend delivery fields

Revision ID: 4d4a85637536
Revises: 72ef3ba5c532
Create Date: 2026-03-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4d4a85637536"
down_revision: Union[str, None] = "72ef3ba5c532"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "invitation_batches",
        sa.Column("campaign_name", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "invitation_batches",
        sa.Column("email_subject", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "invitation_batches",
        sa.Column("email_message", sa.Text(), nullable=True),
    )
    op.add_column(
        "invitation_batches",
        sa.Column("sender_email", sa.String(length=255), nullable=True),
    )

    op.add_column(
        "invitations",
        sa.Column("provider_message_id", sa.String(length=120), nullable=True),
    )
    op.add_column(
        "invitations",
        sa.Column("last_error", sa.Text(), nullable=True),
    )

    op.execute(
        """
        UPDATE invitation_batches
        SET
            campaign_name = COALESCE(campaign_name, 'Legacy Campaign'),
            email_subject = COALESCE(email_subject, 'Legacy Invitation'),
            email_message = COALESCE(email_message, 'Legacy invitation content not available'),
            sender_email = COALESCE(sender_email, 'noreply@mail.quantics.cl')
        """
    )

    op.alter_column("invitation_batches", "campaign_name", nullable=False)
    op.alter_column("invitation_batches", "email_subject", nullable=False)
    op.alter_column("invitation_batches", "email_message", nullable=False)
    op.alter_column("invitation_batches", "sender_email", nullable=False)


def downgrade() -> None:
    op.drop_column("invitations", "last_error")
    op.drop_column("invitations", "provider_message_id")

    op.drop_column("invitation_batches", "sender_email")
    op.drop_column("invitation_batches", "email_message")
    op.drop_column("invitation_batches", "email_subject")
    op.drop_column("invitation_batches", "campaign_name")