"""
main.py

Command-line entry point for Warden.

Usage examples:
    python main.py --provider mock
    python main.py --provider anthropic --model claude-sonnet-4-6
    python main.py --provider openai --category jailbreak
"""

import argparse
from warden.target import get_target
from warden.payloads import get_payloads, list_categories
from warden.runner import run
from warden.report import print_console_report, write_markdown_report


def main():
    parser = argparse.ArgumentParser(
        description="Warden — test an AI system for prompt injection and jailbreak vulnerabilities."
    )
    parser.add_argument(
        "--provider",
        choices=["anthropic", "openai", "mock"],
        default="mock",
        help="Which AI provider to test against. 'mock' requires no API key and is useful for "
             "verifying Warden itself works before testing a real target.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Model name to use (provider-specific). Uses each provider's default if omitted.",
    )
    parser.add_argument(
        "--category",
        default=None,
        choices=list_categories(),
        help="Only run payloads from this category. Runs all categories if omitted.",
    )
    parser.add_argument(
        "--output",
        default="warden_report.md",
        help="Path to write the markdown report to.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="Seconds to wait between requests (avoids rate limiting on real APIs).",
    )

    args = parser.parse_args()

    target_kwargs = {}
    if args.model:
        target_kwargs["model"] = args.model
    target = get_target(args.provider, **target_kwargs)

    payloads = get_payloads(category=args.category)

    print(f"Warden starting: provider={args.provider}, payloads={len(payloads)}\n")

    results = run(target, payloads, delay_seconds=args.delay)

    print_console_report(results)
    report_path = write_markdown_report(results, path=args.output)
    print(f"Full report written to: {report_path}")


if __name__ == "__main__":
    main()
