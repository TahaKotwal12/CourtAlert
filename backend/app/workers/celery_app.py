"""
Celery application and Beat schedule.

Start worker:   celery -A app.workers.celery_app worker --loglevel=info
Start beat:     celery -A app.workers.celery_app beat --loglevel=info

Or combined:    celery -A app.workers.celery_app worker --beat --loglevel=info
"""
from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "courtalert",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Kolkata",
    enable_utc=True,
    # Beat schedule — daily at 8:00 AM IST
    beat_schedule={
        "daily-hearing-alerts": {
            "task": "app.workers.tasks.daily_alert_task",
            "schedule": crontab(hour=23, minute=55),
        },
        "daily-ecourts-sync": {
            "task": "app.workers.tasks.daily_sync_task",
            "schedule": crontab(hour=23, minute=59),  # sync first, then alerts
        },
    },
)
