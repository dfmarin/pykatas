"""Transform raw sandbox JSON into human-readable structured feedback."""

from dataclasses import dataclass


@dataclass
class TestSummary:
    total: int
    passed: int
    failed: int
    errors: int
    failed_names: list[str]


@dataclass
class LintIssue:
    line: int
    col: int
    code: str
    message: str


@dataclass
class ParsedFeedback:
    tests: TestSummary
    lint_issues: list[LintIssue]
    execution_time_ms: int
    has_lint_errors: bool

    @property
    def all_passed(self) -> bool:
        return self.tests.passed == self.tests.total and not self.has_lint_errors


def parse_feedback(raw_json: dict) -> ParsedFeedback:
    report = raw_json.get("tests", {}).get("report", {})
    summary = report.get("summary", {})

    failed_names = [t["nodeid"] for t in report.get("tests", []) if t.get("outcome") == "failed"]

    test_summary = TestSummary(
        total=summary.get("total", 0),
        passed=summary.get("passed", 0),
        failed=summary.get("failed", 0),
        errors=summary.get("error", 0),
        failed_names=failed_names,
    )

    raw_lint = raw_json.get("lint", {}).get("issues", [])
    lint_issues = [
        LintIssue(
            line=issue.get("location", {}).get("row", 0),
            col=issue.get("location", {}).get("column", 0),
            code=issue.get("code", ""),
            message=issue.get("message", ""),
        )
        for issue in raw_lint
    ]

    return ParsedFeedback(
        tests=test_summary,
        lint_issues=lint_issues,
        execution_time_ms=raw_json.get("tests", {}).get("elapsed_ms", 0),
        has_lint_errors=bool(lint_issues),
    )
