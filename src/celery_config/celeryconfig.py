beat_schedule = {  # type: ignore
    "delete-expired-tokens-every-hour": {
        "task": "celery_config.tasks.delete_expired_tokens",
        "schedule": 3600.0,
    },
}

timezone = "UTC"
