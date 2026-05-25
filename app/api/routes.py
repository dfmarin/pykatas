from flask import request, jsonify, abort
from app.extensions import db, kata_loader
from app.models.submission import Submission, SubmissionStatus
from app.services.execution_service import execute_locally  # temp


@api_bp.post("/katas/<kata_id>/submit")
def submit(kata_id: str):
    kata = kata_loader.get(kata_id)
    if not kata:
        abort(404)

    source_code = request.json.get("source_code", "").strip()
    if not source_code:
        return jsonify({"error": "source_code is required"}), 400

    sub = Submission(kata_id=kata_id, source_code=source_code)
    db.session.add(sub)
    db.session.commit()

    # TEMPORARY: synchronous execution, replaced in Step 5
    result = execute_locally(sub, kata)
    sub.status = result.status
    sub.stdout = result.stdout
    sub.stderr = result.stderr
    sub.pytest_output = result.pytest_output
    sub.execution_time_ms = result.execution_time_ms
    db.session.commit()

    return jsonify(sub.to_dict()), 201
