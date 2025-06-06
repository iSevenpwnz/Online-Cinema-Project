from unittest.mock import patch
import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from database.models.accounts import ActivationTokenModel
from celery_config.tasks import delete_expired_tokens

from database.db_sync import SQLLiteSessionLocal


def test_delete_expired_tokens_removes_only_expired(
    memory_session_class, memory_session
):

    with patch(
        "celery_config.tasks.SessionLocal",
        new=memory_session_class,
    ):
        db_session = memory_session

        # Arrange: Add expired and non-expired tokens
        now = datetime.now(timezone.utc)
        expired_token = ActivationTokenModel(
            user_id=1, token="expired", expires_at=now - timedelta(hours=1)
        )
        valid_token = ActivationTokenModel(
            user_id=2, token="valid", expires_at=now + timedelta(hours=1)
        )
        db_session.add_all([expired_token, valid_token])
        db_session.commit()

        # Act: Run the Celery task synchronously
        delete_expired_tokens.run()

        # Assert: Only the valid token remains
        tokens = (
            db_session.execute(select(ActivationTokenModel)).scalars().all()
        )
        token_values = [t.token for t in tokens]

        assert "expired" not in token_values
        assert "valid" in token_values
        assert len(tokens) == 1

        db_session.close()
