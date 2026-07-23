# Warden GUI

> **To start the app: open (double-click) `run.bat` (Windows) or `run.sh`
> (Mac/Linux) in this folder.** That's the whole launch step — it installs
> anything missing and opens the app in your browser automatically.

A local, single-user web app for running Warden without the command line.
Everything runs on your machine — no account, no external service.

## Run it

**Mac/Linux:** double-click `run.sh` (or run `./run.sh` in a terminal).
**Windows:** double-click `run.bat`.

Either one installs Flask automatically on first run if it's missing, then
starts a local server and opens `http://127.0.0.1:5057` in your browser.

If double-clicking doesn't work on your system (some OSes block executing
scripts from Finder/Explorer by default), open a terminal in this folder
and run it manually instead:

```
pip install -r requirements.txt
pip install anthropic     # only if you'll test against Claude
pip install openai        # only if you'll test against GPT
python app.py
```

## Using it

1. Pick a target: **Mock** (no API key, good for a dry run), **Anthropic**,
   or **OpenAI**.
2. For a real provider, enter the model name (optional — defaults are used
   if left blank) and your API key. The key is sent only to your own local
   server for that one run — it is never written to disk or included in
   the report.
3. Choose which OWASP categories to run, set a delay between requests if
   you're worried about rate limits, and click **Run Warden**.
4. Watch results stream in live. When the run finishes, click
   **Download report** for the full markdown report (same format the CLI
   produces).

## Notes

- This wraps the existing `warden/` package unchanged — the GUI is just
  another caller of `runner.run()`, so CLI and GUI stay in sync as the
  payload library grows.
- The dev server Flask prints a warning about is fine for local personal
  use. Don't expose this port to a network — it accepts API keys over
  plain HTTP by design, on the assumption it only ever binds to
  `127.0.0.1`.
