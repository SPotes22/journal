import os

from flask import Flask

from config import Config

from .date_utils import format_day_long, format_weekday_short
from .extensions import db, login_manager, mail


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)
    app.jinja_env.filters["fecha_larga"] = format_day_long
    app.jinja_env.filters["fecha_corta"] = format_weekday_short

    config_object.INSTANCE_DIR.mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    mail.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from .blueprints.auth import auth_bp
    from .blueprints.notifications import notifications_bp
    from .blueprints.tasks import tasks_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(notifications_bp)

    from . import cli

    cli.register(app)

    is_reloader_child = os.environ.get("WERKZEUG_RUN_MAIN") == "true"
    if app.config["MAIL_CONFIGURED"] and (not app.debug or is_reloader_child):
        from .blueprints.notifications.service import start_reminder_scheduler

        start_reminder_scheduler(app)
    else:
        app.logger.info("SMTP no configurado: los recordatorios por email estan desactivados.")

    return app
