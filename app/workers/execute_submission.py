"""RQ job: pull a submission from the DB, run it in the sandbox, persist results."""
import logging
from datetime import datetime, UTC

from app import create_app
from app.extensions import db
from app.models.submission import Submission, SubmissionStatus
from app.services.docker_runner import run_in_sandbox, SandboxError
from app.extensions import kata_loader

logger = logging.getLogger(__name__)


def execute_submission(submission_id: int) -> None:
    app = create_app()
    with app.app_context():
        sub = db.session.get(Submission, submission_id)
        if not sub:
            logger.error("Submission %d not found", submission_id)
            return

        kata = kata_loader.get(sub.kata_id)
        if not kata:
            sub.status = SubmissionStatus.ERROR
            sub.stderr = f"Kata '{sub.kata_id}' not found"
            db.session.commit()
            return

        sub.status = SubmissionStatus.RUNNING
        db.session.commit()

        try:
            result = run_in_sandbox(
                source_code=sub.source_code,
                kata=kata,
                sandbox_image=app.config["SANDBOX_IMAGE"],
                wall_timeout=app.config["SANDBOX_TIMEOUT"],
            )
            sub.status = result.status
            sub.stdout = result.stdout
            sub.stderr = result.stderr
            sub.pytest_output = result.pytest_output
            sub.lint_output = result.lint_output
            sub.execution_time_ms = result.execution_time_ms
        except SandboxError as exc:
            sub.status = SubmissionStatus.ERROR
            sub.stderr = str(exc)
        finally:
            sub.finished_at = datetime.now(UTC)
            db.session.commit()
