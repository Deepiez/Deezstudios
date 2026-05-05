from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "content_studio",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Jakarta",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    # Retry settings
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
    # Beat schedule for periodic tasks
    beat_schedule={
        "process-scheduled-publishes": {
            "task": "app.workers.tasks.process_scheduled_publishes",
            "schedule": 60.0,  # Every minute
        },
        "generate-daily-analytics": {
            "task": "app.workers.tasks.generate_daily_analytics",
            "schedule": 86400.0,  # Every 24 hours
        },
    },
)

celery_app.autodiscover_tasks(["app.workers"])
