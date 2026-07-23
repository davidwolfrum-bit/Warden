# Warden

An open-source tool for testing AI-powered applications for security weaknesses —
prompt injection and jailbreak resistance, mapped to the OWASP Top 10 for LLM Applications.

This repo has two independent things in it:

```
Warden/
├── app/     ← the actual tool (what you download and run)
└── docs/    ← the website + docs (what GitHub Pages serves)
```

They don't depend on each other. `docs/` never imports or runs `app/` — it's a
static page that just links out to wherever the app is downloaded from
(the Releases page). Editing one never risks breaking the other.

## app/ — the tool

A CLI and a local GUI, both thin front ends over the same `warden/` engine
(`target.py`, `payloads.py`, `runner.py`, `evaluator.py`, `report.py`).

```
cd app
pip install -r requirements.txt
python main.py --provider mock          # CLI
python app.py                           # GUI, opens in your browser
```

See `app/README.md` for full usage.

This is what gets zipped and attached to a GitHub Release.

## docs/ — the website

Static HTML/CSS/JS, no build step, no server. GitHub Pages serves this folder
directly if you point Pages at `main` branch → `/docs` in repo Settings →
Pages. That's why it's named `docs` rather than `site` — GitHub recognizes
that folder name as a built-in Pages source.

## Publishing a new version

1. Tag a release (`git tag v0.1.1 && git push --tags`), zip the contents of
   `app/`, attach the zip to the GitHub Release.
2. The download button on the website already links to
   `github.com/<you>/Warden/releases` — nothing to update there per release.
3. Push to `main` — Pages picks up any `docs/` changes automatically.

## Status / things to double check before your first push

- **License**: the website currently says "MIT licensed" but there's no
  `LICENSE` file in this repo yet. Add one (or change the copy) before
  publishing — an unlicensed public repo defaults to "all rights reserved"
  regardless of what the website claims.
- **Windows support**: the website also claims "Windows & Linux" — worth
  confirming that's actually been tested before it goes live, since nothing
  in `app/` currently checks for or excludes either platform.

## Disclaimer

Warden is intended for testing AI systems you own or have explicit
authorization to test. Do not use it against third-party systems without
permission.
