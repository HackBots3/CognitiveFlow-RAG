from celery import Celery
from app.config import settings

celery_app = Celery(
    "cognitiveflow",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "app.ingestion.tasks.*": {"queue": "ingestion"},
    },
)


@celery_app.task(name="ping")
def ping():
    """Health-check task — proves broker + worker + backend all wired."""
    return "pong"
