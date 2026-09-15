import secrets

import click

from .extensions import db
from .models import User

SEED_USERS = [
    {"username": "susana", "display_name": "Susana", "color": "blue"},
    {"username": "santiago", "display_name": "Santiago", "color": "red"},
]


def register(app):
    @app.cli.command("init-db")
    def init_db():
        """Crea las tablas y siembra las cuentas de Susana y Santiago si no existen."""
        db.create_all()
        for data in SEED_USERS:
            if User.query.filter_by(username=data["username"]).first():
                continue
            temp_password = secrets.token_urlsafe(8)
            user = User(
                username=data["username"],
                display_name=data["display_name"],
                color=data["color"],
            )
            user.set_password(temp_password)
            db.session.add(user)
            click.echo(f"Creado usuario '{data['username']}' con contrasena temporal: {temp_password}")
        db.session.commit()
        click.echo("Base de datos lista.")
