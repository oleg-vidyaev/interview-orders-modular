import os

from celery import Celery

celery_app = Celery(
    "shop",
    broker=os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
    include=["app.notifications.tasks"],
)
# tests run tasks in-process, without Redis
celery_app.conf.task_always_eager = os.environ.get("CELERY_EAGER") == "1"
celery_app.conf.task_eager_propagates = True
