from flask import Blueprint, request, jsonify, abort, current_app
from flask_login import login_required, current_user
from redis import Redis
from redis.exceptions import RedisError
from rq import Queue
from app.extensions import db, kata_loader
from app.models.submission import Submission, SubmissionStatus
from app.services.execution_service import execute_locally  # temp
from app.workers.execute_submission import execute_submission


api_bp = Blueprint("api", __name__)


@api_bp.post("/katas/<kata_id>/submit")
@login_required
def submit(kata_id: str):
    kata = kata_loader.get(kata_id)
    if not kata:
        abort(404)

    body = request.get_json(silent=True) or {}
    source_code = body.get("source_code", "").strip()

    if not source_code:
        return jsonify({"error": "source_code is required"}), 400
    if len(source_code.encode()) > 64 * 1024:
        return jsonify({"error": "source_code exceeds 64 KB limit"}), 400

    sub = Submission(
        kata_id=kata_id,
        user_id=current_user.id,
        source_code=source_code,
        status=SubmissionStatus.PENDING,
    )
    db.session.add(sub)
    db.session.commit()

    try:
        redis_conn = Redis.from_url(current_app.config["REDIS_URL"])
        q = Queue("submissions", connection=redis_conn)
        q.enqueue(execute_submission, sub.id, job_timeout=120)
        return jsonify({"id": sub.id, "status": sub.status.value}), 202
    except RedisError as exc:
        if current_app.config.get("DEBUG"):
            result = execute_locally(sub, kata)
            sub.status = result.status
            sub.stdout = result.stdout
            sub.stderr = result.stderr
            sub.pytest_output = result.pytest_output
            sub.execution_time_ms = result.execution_time_ms
            db.session.commit()
            return jsonify({"id": sub.id, "status": sub.status.value, "fallback": "local"}), 200
        raise


@api_bp.get("/submissions/<int:submission_id>")
@login_required
def get_submission(submission_id: int):
    sub = db.session.get(Submission, submission_id)
    if not sub:
        abort(404)
    # Users can only poll their own submissions
    if sub.user_id != current_user.id:
        abort(403)
    return jsonify(sub.to_dict())
