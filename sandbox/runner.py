"""
Runs inside the sandbox container.
Expects:
  /sandbox/solution.py     — user's code
  /sandbox/tests/          — test files
  /sandbox/kata.json       — metadata (timeout, lint rules)
Emits to stdout: JSON result object
"""

import json
import subprocess
import sys
import time
from pathlib import Path


def run_ruff(solution: Path, lint_rules: list[str]) -> dict:
    ignore = ",".join(lint_rules) if lint_rules else None
    cmd = ["ruff", "check", str(solution), "--output-format=json"]
    if ignore:
        cmd += ["--ignore", ignore]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        issues = json.loads(result.stdout)
    except json.JSONDecodeError:
        issues = []
    return {"issues": issues, "raw": result.stdout}


def run_pytest(test_dir: Path, timeout: int) -> dict:
    cmd = [
        "pytest",
        str(test_dir),
        "--tb=short",
        "-q",
        "--no-header",
        "--json-report",
        "--json-report-file=/tmp/report.json",
    ]
    start = time.monotonic()
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    elapsed = int((time.monotonic() - start) * 1000)
    try:
        report = json.loads(Path("/tmp/report.json").read_text())
    except Exception:
        report = {}
    return {
        "passed": result.returncode == 0,
        "stdout": result.stdout[:8000],
        "stderr": result.stderr[:2000],
        "elapsed_ms": elapsed,
        "report": report,
    }


def clean_traceback(output: str) -> str:
    return output.replace("/sandbox/", "").replace("/tmp/kata_job_", "<job>/")


def main() -> None:
    kata_meta = json.loads(Path("/sandbox/kata.json").read_text())
    solution = Path("/sandbox/solution.py")
    test_dir = Path("/sandbox/tests")

    output = {
        "status": "error",
        "lint": {},
        "tests": {},
        "error": None,
    }

    try:
        output["lint"] = run_ruff(solution, kata_meta.get("lint_rules", []))
        test_result = run_pytest(test_dir, kata_meta.get("timeout_seconds", 10))
        output["tests"] = test_result
        output["status"] = "passed" if test_result["passed"] else "failed"
    except subprocess.TimeoutExpired:
        output["status"] = "timeout"
        output["error"] = "Execution exceeded time limit."
    except Exception as exc:
        output["status"] = "error"
        output["error"] = str(exc)

    print(json.dumps(clean_traceback(output)))


if __name__ == "__main__":
    main()
