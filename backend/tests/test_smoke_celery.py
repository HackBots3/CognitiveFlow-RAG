"""End-to-end Celery test — proves broker + worker + backend all wired."""
import time
from app.workers.celery_app import ping


def test_celery_ping_task_executes():
    """Enqueue ping task, get pong back from worker via Redis backend."""
    result = ping.delay()
    time.sleep(2)
    val = result.get(timeout=10)
    assert val == "pong"
