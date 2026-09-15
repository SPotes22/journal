from datetime import date, datetime, timedelta

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ...extensions import db
from ...models import Task
from . import tasks_bp


def _parse_date(value, default=None):
    if not value:
        return default
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return default


def _parse_time(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%H:%M").time()
    except ValueError:
        return None


def _week_start(d):
    return d - timedelta(days=d.weekday())


def _get_owned_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.created_by_id != current_user.id:
        abort(403)
    return task


@tasks_bp.route("/")
@login_required
def today():
    return redirect(url_for("tasks.day_view", date_str=date.today().isoformat()))


@tasks_bp.route("/day/<date_str>")
@login_required
def day_view(date_str):
    day = _parse_date(date_str, default=date.today())
    tasks = (
        Task.query.filter_by(date=day)
        .order_by(Task.time.is_(None), Task.time)
        .all()
    )
    return render_template(
        "tasks/day.html",
        day=day,
        tasks=tasks,
        prev_day=(day - timedelta(days=1)).isoformat(),
        next_day=(day + timedelta(days=1)).isoformat(),
    )


@tasks_bp.route("/week/<date_str>")
@login_required
def week_view(date_str):
    anchor = _parse_date(date_str, default=date.today())
    start = _week_start(anchor)
    days = [start + timedelta(days=i) for i in range(7)]
    tasks_by_day = {
        d: Task.query.filter_by(date=d).order_by(Task.time.is_(None), Task.time).all()
        for d in days
    }
    return render_template(
        "tasks/week.html",
        days=days,
        tasks_by_day=tasks_by_day,
        prev_week=(start - timedelta(days=7)).isoformat(),
        next_week=(start + timedelta(days=7)).isoformat(),
    )


@tasks_bp.route("/tasks", methods=["POST"])
@login_required
def create_task():
    title = request.form.get("title", "").strip()
    task_date = _parse_date(request.form.get("date", ""))
    notes = request.form.get("notes", "").strip()

    if not title or not task_date:
        flash("Titulo y fecha son obligatorios.", "error")
        return redirect(request.referrer or url_for("tasks.today"))

    task = Task(
        title=title,
        notes=notes or None,
        date=task_date,
        time=_parse_time(request.form.get("time", "")),
        created_by_id=current_user.id,
    )
    db.session.add(task)
    db.session.commit()
    return redirect(url_for("tasks.day_view", date_str=task_date.isoformat()))


@tasks_bp.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = _get_owned_task(task_id)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        task_date = _parse_date(request.form.get("date", ""))
        notes = request.form.get("notes", "").strip()

        if not title or not task_date:
            flash("Titulo y fecha son obligatorios.", "error")
        else:
            task.title = title
            task.date = task_date
            task.time = _parse_time(request.form.get("time", ""))
            task.notes = notes or None
            db.session.commit()
            return redirect(url_for("tasks.day_view", date_str=task_date.isoformat()))

    return render_template("tasks/edit.html", task=task)


@tasks_bp.route("/tasks/<int:task_id>/toggle", methods=["POST"])
@login_required
def toggle_task(task_id):
    task = _get_owned_task(task_id)
    task.is_done = not task.is_done
    db.session.commit()
    return redirect(request.referrer or url_for("tasks.day_view", date_str=task.date.isoformat()))


@tasks_bp.route("/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    task = _get_owned_task(task_id)
    day_str = task.date.isoformat()
    db.session.delete(task)
    db.session.commit()
    return redirect(request.referrer or url_for("tasks.day_view", date_str=day_str))
