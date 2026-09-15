from flask import Blueprint
from flask_login import current_user

from .service import get_due_reminders

notifications_bp = Blueprint("notifications", __name__)


@notifications_bp.app_context_processor
def inject_due_reminders():
    if current_user.is_authenticated:
        return {"due_reminders": get_due_reminders(current_user)}
    return {"due_reminders": []}
