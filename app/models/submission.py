import enum
from datetime import datetime, UTC
from app.extensions import db


class SubmissionStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    TIMEOUT = "timeout"


class Submission(db.Model):
    __tablename__ = "submissions"

    id = db.Column(db.Integer, primary_key=True)
    kata_id = db.Column(db.String(64), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # null until Step 7
    source_code = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum(SubmissionStatus), default=SubmissionStatus.PENDING, nullable=False)
    stdout = db.Column(db.Text)
    stderr = db.Column(db.Text)
    pytest_output = db.Column(db.Text)
    lint_output = db.Column(db.Text)
    execution_time_ms = db.Column(db.Integer)
    feedback_json = db.Column(db.JSON)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC))
    finished_at = db.Column(db.DateTime(timezone=True))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "kata_id": self.kata_id,
            "status": self.status.value,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "pytest_output": self.pytest_output,
            "lint_output": self.lint_output,
            "execution_time_ms": self.execution_time_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
