import json
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

from app.models.submission import SubmissionStatus
from app.services.kata_loader import KataDefinition


@dataclass
class SandboxResult:
    status: SubmissionStatus
    stdout: str
    stderr: str
    pytest_output: str
    lint_output: str
    execution_time_ms: int
    raw_json: dict


class SandboxError(Exception):
    pass


def run_in_sandbox(
    source_code: str,
    kata: KataDefinition,
    sandbox_image: str,
    wall_timeout: int = 60,
) -> SandboxResult:
    with tempfile.TemporaryDirectory(prefix="kata_job_") as tmpdir:
        job_dir = Path(tmpdir)

        # Write user code
        (job_dir / "solution.py").write_text(source_code)

        # Write kata metadata
        (job_dir / "kata.json").write_text(
            json.dumps(
                {
                    "timeout_seconds": kata.timeout_seconds,
                    "lint_rules": kata.lint_rules,
                }
            )
        )

        # Copy tests
        test_dst = job_dir / "tests"
        test_dst.mkdir()
        test_src = kata.kata_dir / "tests"
        for f in test_src.glob("*.py"):
            shutil.copy(f, test_dst / f.name)

        start = time.monotonic()
        try:
            proc = subprocess.run(
                [
                    "docker",
                    "run",
                    "--rm",
                    "--network",
                    "none",
                    "--memory",
                    f"{kata.memory_limit_mb}m",
                    "--memory-swap",
                    f"{kata.memory_limit_mb}m",
                    "--cpus",
                    "0.5",
                    "--pids-limit",
                    "64",
                    "--read-only",
                    "--tmpfs",
                    "/tmp:size=32m",
                    "-v",
                    f"{job_dir}:/sandbox:ro",
                    sandbox_image,
                ],
                capture_output=True,
                text=True,
                timeout=wall_timeout,
            )
            elapsed = int((time.monotonic() - start) * 1000)
        except subprocess.TimeoutExpired:
            return SandboxResult(
                status=SubmissionStatus.TIMEOUT,
                stdout="",
                stderr="Wall-clock timeout exceeded.",
                pytest_output="",
                lint_output="",
                execution_time_ms=wall_timeout * 1000,
                raw_json={},
            )

        if proc.returncode not in (0, 1):
            raise SandboxError(f"Docker exited {proc.returncode}: {proc.stderr[:1000]}")

        try:
            raw = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:
            raise SandboxError(f"Invalid JSON from sandbox: {exc}\n{proc.stdout[:500]}")

        status_map = {
            "passed": SubmissionStatus.PASSED,
            "failed": SubmissionStatus.FAILED,
            "timeout": SubmissionStatus.TIMEOUT,
            "error": SubmissionStatus.ERROR,
        }

        return SandboxResult(
            status=status_map.get(raw.get("status", "error"), SubmissionStatus.ERROR),
            stdout=raw.get("tests", {}).get("stdout", ""),
            stderr=raw.get("tests", {}).get("stderr", ""),
            pytest_output=raw.get("tests", {}).get("stdout", ""),
            lint_output=json.dumps(raw.get("lint", {})),
            execution_time_ms=raw.get("tests", {}).get("elapsed_ms", elapsed),
            raw_json=raw,
        )
