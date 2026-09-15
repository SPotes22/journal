import logging
from datetime import date, datetime, timedelta

from ...extensions import db, mail
from ...models import Task

logger = logging.getLogger(__name__)
_scheduler = None


def get_due_reminders(user):
    return (
        Task.query.filter_by(created_by_id=user.id, date=date.today(), is_done=False)
        .order_by(Task.time.is_(None), Task.time)
        .all()
    )


def _send_pending_reminders(app):
    from flask_mail import Message

    with app.app_context():
        window_end = datetime.now() + timedelta(minutes=app.config["REMINDER_WINDOW_MINUTES"])
        due_tasks = Task.query.filter_by(date=date.today(), is_done=False, reminder_sent=False).all()

        for task in due_tasks:
            if task.time is None:
                continue
            task_datetime = datetime.combine(task.date, task.time)
            if task_datetime > window_end:
                continue

            recipient = task.creator.email
            if not recipient:
                continue

            try:
                message = Message(
                    subject=f"Recordatorio: {task.title}",
                    recipients=[recipient],
                    body=(
                        f"Hola {task.creator.display_name}, tu tarea '{task.title}' "
                        f"esta programada para hoy a las {task.time.strftime('%H:%M')}."
                    ),
                )
                mail.send(message)
                task.reminder_sent = True
                db.session.commit()
            except Exception:
                logger.exception("No se pudo enviar el recordatorio por email para la tarea %s", task.id)


def start_reminder_scheduler(app):
    global _scheduler
    from apscheduler.schedulers.background import BackgroundScheduler

    if _scheduler is not None:
        return _scheduler

    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(
        lambda: _send_pending_reminders(app),
        "interval",
        minutes=app.config["REMINDER_CHECK_INTERVAL_MINUTES"],
        id="send_task_reminders",
    )
    scheduler.start()
    _scheduler = scheduler
    return scheduler
