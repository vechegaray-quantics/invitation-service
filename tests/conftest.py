import pytest
from sqlalchemy import delete

from app.db import SessionLocal
from app.models.audience_participant import AudienceParticipant
from app.models.invitation import Invitation
from app.models.invitation_batch import InvitationBatch


@pytest.fixture(autouse=True)
def clean_tables() -> None:
    with SessionLocal() as session:
        session.execute(delete(Invitation))
        session.execute(delete(InvitationBatch))
        session.execute(delete(AudienceParticipant))
        session.commit()