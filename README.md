# Warden

An open-source tool for testing AI-powered applications for security weaknesses — starting with prompt injection and jailbreak resistance.

## What it does

Companies shipping AI features (chatbots, AI agents, AI-powered support tools) need to know whether their system can be manipulated into ignoring its instructions, leaking data it shouldn't, or taking actions it wasn't meant to take. Warden automates that testing: point it at a target AI system, it runs a library of known adversarial prompts against it, and reports which ones succeeded — i.e., which ones are real vulnerabilities.

This is the same category of tool as open-source projects like [Garak](https://github.com/leondz/garak) and Microsoft's [PyRIT](https://github.com/Azure/PyRIT) — Warden is my own build of this concept, developed as part of learning AI security hands-on.

## Why this exists

This project is part of my path into AI security engineering. Rather than only using existing red-teaming tools, I'm building my own from the ground up to actually understand how they work under the hood — the same build → break → understand → fix loop I've used on earlier projects, applied to AI systems instead of traditional web apps.

## How it works

1. **Target** — connects to a real AI system (via its API) that's being tested
2. **Payload library** — a categorized set of known prompt injection and jailbreak attempts
3. **Runner** — sends each payload to the target and collects the responses
4. **Evaluator** — determines whether each response counts as a pass (AI resisted) or fail (AI was manipulated)
5. **Report** — summarizes results, mapped to the [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/) where relevant

## Status

🚧 Early development. Currently building out the core pipeline (target connector → payload library → runner → evaluator → report).

## Roadmap

- [ ] Basic target connector (single AI provider)
- [ ] Starter payload library (core prompt injection patterns)
- [ ] Test runner + simple keyword-based evaluator
- [ ] Readable report output
- [ ] Expanded payload categories
- [ ] Smarter (LLM-based) evaluation
- [ ] Config file support for custom targets/tests
- [ ] Agent / tool-use specific test cases
- [ ] RAG-specific test cases

## Usage

*(coming soon — not yet functional)*

## Disclaimer

Warden is intended for testing AI systems you own or have explicit authorization to test. Do not use it against third-party systems without permission.

## About

Built as part of my ongoing cybersecurity learning journey, alongside other projects in my [WoldavSiteDevTools](https://github.com/davidwolfrum-bit/WoldavSiteDevTools) repo.

## Download here-> 

https://davidwolfrum-bit.github.io/Warden/
