"""
WARNING: This module executes arbitrary user code via subprocess.
It is ONLY for TEMPORARY local development, and will be replaced by a container.
NEVER deploy this to production.
"""

import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from app.services.kata_loader import KataDefinition
from app.models.submission import Submission, SubmissionStatus


@dataclass
class ExecutionResult:
    status: SubmissionStatus
    stdout: str
    stderr: str
    pytest_output: str
    execution_time_ms: int


def execute_locally(submission: Submission, kata: KataDefinition) -> ExecutionResult:
    """Subprocess-based execution. DEV ONLY."""
    with tempfile.TemporaryDirectory(prefix="kata_") as tmpdir:
        tmp = Path(tmpdir)
        solution_file = tmp / "solution.py"
        solution_file.write_text(submission.source_code)

        # Copy kata tests into temp dir
        test_src = kata.kata_dir / "tests"
        test_dst = tmp / "tests"
        test_dst.mkdir()
        for f in test_src.glob("test_public*.py"):
            (test_dst / f.name).write_text(f.read_text())

        start = time.monotonic()
        try:
            result = subprocess.run(
                ["pytest", str(test_dst), "--tb=short", "-q"],
                capture_output=True,
                text=True,
                timeout=kata.timeout_seconds,
                cwd=str(tmp),
            )
            elapsed = int((time.monotonic() - start) * 1000)
            status = SubmissionStatus.PASSED if result.returncode == 0 else SubmissionStatus.FAILED
            return ExecutionResult(
                status=status,
                stdout=result.stdout[:5000],
                stderr=result.stderr[:5000],
                pytest_output=result.stdout[:5000],
                execution_time_ms=elapsed,
            )
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                status=SubmissionStatus.TIMEOUT,
                stdout="",
                stderr="Execution timed out.",
                pytest_output="",
                execution_time_ms=kata.timeout_seconds * 1000,
            )
