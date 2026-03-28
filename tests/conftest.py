import pytest
from sqlalchemy import delete

from app.db import SessionLocal
from app.models.audience_participant import AudienceParticipant


@pytest.fixture(autouse=True)
def clean_audience_table() -> None:
    with SessionLocal() as session:
        session.execute(delete(AudienceParticipant))
        session.commit()