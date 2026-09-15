from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from ...extensions import db
from ...models import User
from . import auth_bp


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("tasks.today"))

    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("tasks.today"))

        flash("Usuario o contrasena incorrectos.", "error")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")

        if not current_user.check_password(current_password):
            flash("La contrasena actual no es correcta.", "error")
        elif len(new_password) < 6:
            flash("La nueva contrasena debe tener al menos 6 caracteres.", "error")
        else:
            current_user.set_password(new_password)
            db.session.commit()
            flash("Contrasena actualizada.", "success")
            return redirect(url_for("tasks.today"))

    return render_template("auth/change_password.html")
