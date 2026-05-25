from flask import request, jsonify, abort
from flask_login import login_required, current_user
from redis import Redis
from rq import Queue
from app.extensions import db, kata_loader
from app.models.submission import Submission, SubmissionStatus
from app.services.execution_service import execute_locally  # temp
from app.workers.execute_submission import execute_submission


@api_bp.post("/katas/<kata_id>/submit")
@login_required
def submit(kata_id: str):
    kata = kata_loader.get(kata_id)
    if not kata:
        abort(404)

    source_code = request.json.get("source_code", "").strip()
    if not source_code:
        return jsonify({"error": "source_code is required"}), 400

    sub = Submission(
        kata_id=kata_id,
        source_code=source_code,
        user_id=current_user.id,
        status=SubmissionStatus.PENDING,
    )
    db.session.add(sub)
    db.session.commit()

    redis_conn = Redis.from_url(current_app.config["REDIS_URL"])
    q = Queue("submissions", connection=redis_conn)
    q.enqueue(execute_submission, sub.id, job_timeout=120)

    return jsonify({"id": sub.id, "status": sub.status.value}), 202


@api_bp.get("/submissions/<int:submission_id>")
def submission_status(submission_id: int):
    sub = db.session.get(Submission, submission_id)
    if not sub:
        abort(404)
    return jsonify(sub.to_dict())
