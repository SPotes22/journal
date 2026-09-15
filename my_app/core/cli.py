import os
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
        """Crea las tablas y siembra/actualiza las cuentas de Susana y Santiago.

        La contrasena de cada cuenta se toma de la variable de entorno
        <USUARIO>_PASSWORD (ej. SUSANA_PASSWORD en .env) si esta definida.
        Si no esta definida: para un usuario nuevo se genera una temporal
        (se imprime en consola); para uno existente no se toca su contrasena.
        """
        db.create_all()
        for data in SEED_USERS:
            env_password = os.environ.get(f"{data['username'].upper()}_PASSWORD")
            user = User.query.filter_by(username=data["username"]).first()

            if user is None:
                password = env_password or secrets.token_urlsafe(8)
                user = User(
                    username=data["username"],
                    display_name=data["display_name"],
                    color=data["color"],
                )
                user.set_password(password)
                db.session.add(user)
                if env_password:
                    click.echo(f"Creado usuario '{data['username']}' con la contrasena de .env.")
                else:
                    click.echo(f"Creado usuario '{data['username']}' con contrasena temporal: {password}")
            elif env_password:
                user.set_password(env_password)
                click.echo(f"Actualizada la contrasena de '{data['username']}' desde .env.")

        db.session.commit()
        click.echo("Base de datos lista.")
