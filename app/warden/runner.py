"""
runner.py

Orchestrates a full test run: takes a target and a list of payloads,
sends each one, evaluates the response, and returns the full set of
results for reporting.
"""

import time
from warden.target import Target
from warden.payloads import Payload
from warden.evaluator import evaluate, EvaluationResult, Confidence


def run(
    target: Target,
    payloads: list[Payload],
    delay_seconds: float = 0.5,
    verbose: bool = True,
    on_result=None,
) -> list[EvaluationResult]:
    """
    Send each payload to the target, evaluate the response, and
    return all results.

    delay_seconds: pause between requests, to avoid hammering a real
    API (and getting rate-limited) during a test run.

    on_result: optional callback invoked as on_result(index, total, result)
    after each payload completes. Lets a caller (e.g. a GUI) show live
    progress without duplicating this loop. Never required by the CLI.
    """
    results: list[EvaluationResult] = []

    for i, payload in enumerate(payloads, start=1):
        if verbose:
            print(f"[{i}/{len(payloads)}] Running '{payload.name}' ({payload.category})...")

        if not payload.prompt.strip():
            if verbose:
                print(f"    SKIPPED — '{payload.name}' is a placeholder (testable=False) with no prompt.")
            results.append(
                EvaluationResult(
                    payload=payload,
                    response="<skipped: placeholder payload, no prompt to send>",
                    passed=True,
                    confidence=Confidence.LOW,
                    reason="This category is not runtime-testable via a single prompt "
                           "(see payload description) — tracked for coverage, not run.",
                )
            )
            continue

        try:
            response = target.send(payload.prompt)
        except Exception as e:
            if verbose:
                print(f"    ERROR sending payload: {e}")
            error_result = EvaluationResult(
                payload=payload,
                response=f"<error: {e}>",
                passed=True,  # can't confirm a failure if the request itself errored
                confidence=Confidence.LOW,
                reason="Request failed before a response was received — treat as inconclusive, not a pass.",
            )
            results.append(error_result)
            if on_result:
                on_result(i, len(payloads), error_result)
            continue

        result = evaluate(payload, response)
        results.append(result)
        if on_result:
            on_result(i, len(payloads), result)

        if verbose:
            status = "PASS" if result.passed else "FAIL"
            print(f"    {status} — {result.reason}")

        if delay_seconds > 0 and i < len(payloads):
            time.sleep(delay_seconds)

    return results
