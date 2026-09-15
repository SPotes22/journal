from datetime import date

from flask import Blueprint

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.app_context_processor
def inject_today():
    return {"today": date.today()}


from . import routes  # noqa: E402,F401
