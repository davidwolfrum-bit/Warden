"""
app.py

Local web-app GUI for Warden. Run with `python app.py` — it starts a
server on localhost and opens the dashboard in your default browser.
No account, no external service: everything runs on your machine and
talks directly to whichever provider you point it at.

This file is a thin layer on top of the existing warden/ package
(target, payloads, runner, evaluator, report) — it doesn't reimplement
any of that logic, just orchestrates it for a browser UI instead of
the CLI.
"""

import os
import threading
import uuid
import webbrowser
from dataclasses import asdict

from flask import Flask, jsonify, render_template, request, send_file, abort

from warden.target import get_target
from warden.payloads import get_payloads, list_categories, PAYLOADS
from warden.runner import run as run_warden
from warden.report import summarize, write_markdown_report

app = Flask(__name__)

# In-memory run registry. This is a single-user local tool (like the
# CLI it wraps) — no database, no persistence across restarts needed.
RUNS: dict[str, dict] = {}
RUNS_LOCK = threading.Lock()


def _result_to_dict(index, total, result) -> dict:
    return {
        "index": index,
        "total": total,
        "name": result.payload.name,
        "owasp_id": result.payload.owasp_id,
        "owasp_name": result.payload.owasp_name,
        "category": result.payload.category,
        "severity": result.payload.severity.value,
        "passed": result.passed,
        "confidence": result.confidence.value,
        "reason": result.reason,
        "prompt": result.payload.prompt,
        "response": result.response,
    }


def _execute_run(run_id: str, config: dict):
    state = RUNS[run_id]
    try:
        target_kwargs = {}
        if config.get("model"):
            target_kwargs["model"] = config["model"]
        if config.get("api_key"):
            target_kwargs["api_key"] = config["api_key"]

        target = get_target(config["provider"], **target_kwargs)

        categories = config.get("categories")
        if categories:
            payloads = [p for p in get_payloads() if p.category in categories]
        else:
            payloads = get_payloads()

        with RUNS_LOCK:
            state["total"] = len(payloads)
            state["status"] = "running"

        def on_result(index, total, result):
            with RUNS_LOCK:
                state["completed"] = index
                state["results"].append(_result_to_dict(index, total, result))

        results = run_warden(
            target,
            payloads,
            delay_seconds=config.get("delay", 0.5),
            verbose=False,
            on_result=on_result,
        )

        with RUNS_LOCK:
            state["raw_results"] = results
            state["summary"] = summarize(results)
            state["status"] = "complete"

    except Exception as e:
        with RUNS_LOCK:
            state["status"] = "error"
            state["error"] = str(e)


@app.route("/")
def index():
    categories = list_categories()
    testable_counts = {c: len(get_payloads(category=c)) for c in categories}
    return render_template(
        "index.html",
        categories=categories,
        testable_counts=testable_counts,
        total_payloads=len(get_payloads()),
    )


@app.route("/api/run", methods=["POST"])
def start_run():
    config = request.get_json(force=True) or {}

    provider = config.get("provider", "mock")
    if provider not in ("mock", "anthropic", "openai"):
        return jsonify({"error": f"Unknown provider '{provider}'"}), 400

    run_id = uuid.uuid4().hex[:12]
    with RUNS_LOCK:
        RUNS[run_id] = {
            "status": "starting",
            "total": 0,
            "completed": 0,
            "results": [],
            "raw_results": None,
            "summary": None,
            "error": None,
            "report_path": None,
        }

    thread = threading.Thread(target=_execute_run, args=(run_id, config), daemon=True)
    thread.start()

    return jsonify({"run_id": run_id})


@app.route("/api/status/<run_id>")
def run_status(run_id):
    with RUNS_LOCK:
        state = RUNS.get(run_id)
        if state is None:
            abort(404)
        # Don't serialize raw_results (EvaluationResult objects) over JSON.
        payload = {k: v for k, v in state.items() if k != "raw_results"}
    return jsonify(payload)


@app.route("/api/report/<run_id>")
def download_report(run_id):
    with RUNS_LOCK:
        state = RUNS.get(run_id)
        if state is None or state["status"] != "complete":
            abort(404)
        raw_results = state["raw_results"]

    reports_dir = os.path.join(os.path.dirname(__file__), "reports")
    os.makedirs(reports_dir, exist_ok=True)
    path = os.path.join(reports_dir, f"warden_report_{run_id}.md")
    write_markdown_report(raw_results, path=path)

    return send_file(path, as_attachment=True, download_name="warden_report.md")


def main():
    port = 5057
    url = f"http://127.0.0.1:{port}"
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    print(f"Warden GUI running at {url} (Ctrl+C to stop)")
    app.run(host="127.0.0.1", port=port, debug=False)


if __name__ == "__main__":
    main()
