from flask import Blueprint, jsonify, request
from sqlalchemy import text

from .models import Task, db

bp = Blueprint("api", __name__)


@bp.get("/health")
def health():
    # Docker healthcheck hits this; it also verifies the database is reachable
    db.session.execute(text("SELECT 1"))
    return jsonify(status="ok")


@bp.get("/tasks")
def list_tasks():
    tasks = Task.query.order_by(Task.id).all()
    return jsonify([t.to_dict() for t in tasks])


@bp.post("/tasks")
def create_task():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify(error="title is required"), 400

    task = Task(title=title)
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


@bp.get("/tasks/<int:task_id>")
def get_task(task_id):
    task = db.get_or_404(Task, task_id)
    return jsonify(task.to_dict())


@bp.patch("/tasks/<int:task_id>")
def update_task(task_id):
    task = db.get_or_404(Task, task_id)
    data = request.get_json(silent=True) or {}

    if "title" in data:
        title = (data["title"] or "").strip()
        if not title:
            return jsonify(error="title cannot be empty"), 400
        task.title = title
    if "done" in data:
        task.done = bool(data["done"])

    db.session.commit()
    return jsonify(task.to_dict())


@bp.delete("/tasks/<int:task_id>")
def delete_task(task_id):
    task = db.get_or_404(Task, task_id)
    db.session.delete(task)
    db.session.commit()
    return "", 204
