"""
report.py

Turns a list of EvaluationResults into a human-readable report,
both as a console summary and a saved markdown file.
"""

from datetime import datetime
from warden.evaluator import EvaluationResult, Confidence


def _safe_code_block(text: str) -> str:
    """
    Wrap text in a markdown code fence that won't be broken by ``` inside
    the text itself (common with jailbreak payloads that ask for code,
    or responses that happen to contain triple backticks).
    """
    # Use a fence longer than any backtick run already present in the text.
    longest_run = 0
    current_run = 0
    for ch in text:
        if ch == "`":
            current_run += 1
            longest_run = max(longest_run, current_run)
        else:
            current_run = 0
    fence = "`" * max(3, longest_run + 1)
    return f"{fence}\n{text}\n{fence}"


def summarize(results: list[EvaluationResult]) -> dict:
    """Compute basic stats from a set of results."""
    total = len(results)
    failed = [r for r in results if not r.passed]
    passed = [r for r in results if r.passed]
    needs_review = [r for r in results if r.confidence == Confidence.LOW]

    by_category: dict[str, dict[str, int]] = {}
    by_owasp: dict[str, dict[str, int]] = {}
    by_severity_failed: dict[str, int] = {}

    for r in results:
        cat = r.payload.category
        by_category.setdefault(cat, {"passed": 0, "failed": 0})
        owasp_key = f"{r.payload.owasp_id} — {r.payload.owasp_name}"
        by_owasp.setdefault(owasp_key, {"passed": 0, "failed": 0})

        if r.passed:
            by_category[cat]["passed"] += 1
            by_owasp[owasp_key]["passed"] += 1
        else:
            by_category[cat]["failed"] += 1
            by_owasp[owasp_key]["failed"] += 1
            sev = r.payload.severity.value
            by_severity_failed[sev] = by_severity_failed.get(sev, 0) + 1

    return {
        "total": total,
        "passed": len(passed),
        "failed": len(failed),
        "needs_review": len(needs_review),
        "by_category": by_category,
        "by_owasp": by_owasp,
        "by_severity_failed": by_severity_failed,
    }


def print_console_report(results: list[EvaluationResult]) -> None:
    """Print a summary directly to the console."""
    stats = summarize(results)

    print("\n" + "=" * 60)
    print("WARDEN TEST REPORT")
    print("=" * 60)
    print(f"Total payloads run: {stats['total']}")
    print(f"Passed (target resisted): {stats['passed']}")
    print(f"Failed (target compromised): {stats['failed']}")
    print(f"Flagged for manual review (low confidence): {stats['needs_review']}")

    if stats["by_severity_failed"]:
        print("\nFailures by severity:")
        for sev in ["critical", "high", "medium", "low"]:
            if sev in stats["by_severity_failed"]:
                print(f"  {sev.upper()}: {stats['by_severity_failed'][sev]}")

    print("\nBy OWASP LLM Top 10 category:")
    for owasp_key, counts in stats["by_owasp"].items():
        print(f"  {owasp_key}: {counts['passed']} passed / {counts['failed']} failed")

    failures = [r for r in results if not r.passed]
    if failures:
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        failures.sort(key=lambda r: severity_order.get(r.payload.severity.value, 99))
        print("\n--- FAILURES (needs attention, worst first) ---")
        for r in failures:
            print(f"\n[{r.payload.severity.value.upper()}] {r.payload.owasp_id} — {r.payload.name}")
            print(f"  Prompt: {r.payload.prompt[:100]}...")
            print(f"  Reason: {r.reason}")
            print(f"  Response snippet: {r.response[:150]}...")

    review_needed = [r for r in results if r.confidence == Confidence.LOW]
    if review_needed:
        print(f"\n--- {len(review_needed)} RESULT(S) NEED MANUAL REVIEW (low confidence) ---")
        for r in review_needed:
            print(f"  {r.payload.owasp_id} — {r.payload.name}: read the raw response before trusting this verdict")

    print("=" * 60 + "\n")


def write_markdown_report(results: list[EvaluationResult], path: str = "warden_report.md") -> str:
    """Write a full markdown report to disk and return the path."""
    stats = summarize(results)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        "# Warden Test Report",
        "",
        f"Generated: {timestamp}",
        "",
        "## Summary",
        "",
        f"- Total payloads run: {stats['total']}",
        f"- Passed (target resisted): {stats['passed']}",
        f"- Failed (target compromised): {stats['failed']}",
        f"- Flagged for manual review (low confidence): {stats['needs_review']}",
        "",
    ]

    if stats["by_severity_failed"]:
        lines.append("## Failures by severity")
        lines.append("")
        for sev in ["critical", "high", "medium", "low"]:
            if sev in stats["by_severity_failed"]:
                lines.append(f"- **{sev.upper()}**: {stats['by_severity_failed'][sev]}")
        lines.append("")

    lines.append("## Coverage by OWASP Top 10 for LLM Applications")
    lines.append("")
    for owasp_key, counts in stats["by_owasp"].items():
        lines.append(f"- **{owasp_key}**: {counts['passed']} passed / {counts['failed']} failed")

    lines.append("")
    lines.append("## Detailed results")
    lines.append("")

    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    sorted_results = sorted(
        results,
        key=lambda r: (r.passed, severity_order.get(r.payload.severity.value, 99)),
    )

    for r in sorted_results:
        status = "PASS" if r.passed else "FAIL"
        confidence_note = " (NEEDS MANUAL REVIEW)" if r.confidence.value == "low" else ""
        lines.append(
            f"### {status} — {r.payload.owasp_id} {r.payload.owasp_name} — "
            f"{r.payload.name} (severity: {r.payload.severity.value}){confidence_note}"
        )
        lines.append("")
        lines.append(f"**Description:** {r.payload.description}")
        lines.append("")
        lines.append("**Prompt sent:**")
        lines.append(_safe_code_block(r.payload.prompt))
        lines.append("")
        lines.append("**Response received:**")
        lines.append(_safe_code_block(r.response))
        lines.append("")
        lines.append(f"**Evaluator reasoning ({r.confidence.value} confidence):** {r.reason}")
        lines.append("")
        lines.append("---")
        lines.append("")

    content = "\n".join(lines)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return path
