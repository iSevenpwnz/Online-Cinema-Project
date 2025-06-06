from celery_config.celery_worker import celery_app
from datetime import datetime, timezone
from database.models.accounts import ActivationTokenModel
from database.db_sync import SessionLocal


@celery_app.task
def delete_expired_tokens():
    db = SessionLocal()
    try:
        deleted = (
            db.query(ActivationTokenModel)
            .filter(
                ActivationTokenModel.expires_at < datetime.now(timezone.utc)
            )
            .delete()
        )
        db.commit()
        print(f"Deleted {deleted} expired tokens")
    finally:
        db.close()
