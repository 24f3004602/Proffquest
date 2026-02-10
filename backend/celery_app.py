import os
from celery import Celery
from celery.schedules import crontab

celery = Celery(__name__)


def make_celery(app):
    broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

    celery.main = app.import_name
    celery.conf.update(
        broker_url=broker_url,
        result_backend=result_backend,
        timezone=os.getenv("CELERY_TIMEZONE", "UTC"),
        enable_utc=True,
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super().__call__(*args, **kwargs)

    celery.Task = ContextTask

    celery.conf.beat_schedule = {
        "interview-reminders-hourly": {
            "task": "tasks.send_interview_reminders",
            "schedule": crontab(minute=0),
        },
        "deadline-reminders-daily": {
            "task": "tasks.send_deadline_reminders",
            "schedule": crontab(minute=0, hour=9),
        },
        "monthly-placement-reports": {
            "task": "tasks.generate_monthly_placement_reports",
            "schedule": crontab(minute=0, hour=3, day_of_month=1),
        },
        "monthly-admin-activity-report": {
            "task": "tasks.generate_admin_monthly_report",
            "schedule": crontab(minute=0, hour=3, day_of_month=1),
        },
    }

    return celery


import tasks
