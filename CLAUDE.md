# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

"Spendly" is a Flask expense-tracker web app built as a **step-by-step teaching scaffold**. Large parts are intentionally unimplemented: `app.py` contains placeholder routes that return strings like `"Add expense — coming in Step 7"`, and `database/db.py` is a stub with only a docstring describing the three functions students must write. When editing, respect that phased structure — don't implement a later "Step" unless asked.

## Commands

The repo ships a committed virtualenv at `cldvenv/` (Windows). Activate it, or create a fresh one:

```bash
# use committed venv
cldvenv/Scripts/activate            # Git Bash on Windows
# or fresh
python -m venv venv && venv/Scripts/activate
pip install -r requirements.txt
```

- **Run the app:** `python app.py` — serves on `http://localhost:5001` with `debug=True` (there is no `flask run` config; the port is hardcoded).
- **Tests:** `pytest` (`pytest-flask` is available). No test files exist yet; place them at repo root or in a `tests/` dir. Run one test with `pytest path/to/test_file.py::test_name`.

There is no build step, linter, or formatter configured.

## Architecture

**Server-rendered Flask, no framework beyond Flask itself.** Three layers:

1. **`app.py`** — the entire application: `Flask(__name__)`, all route definitions, run block. No blueprints, no app factory. New routes go here.
2. **`database/db.py`** — SQLite access layer (currently a stub). Intended contract: `get_db()` returns a connection with `row_factory` set and foreign keys enabled; `init_db()` runs `CREATE TABLE IF NOT EXISTS`; `seed_db()` inserts dev sample data. The DB file is `expense_tracker.db` at repo root (gitignored).
3. **`templates/`** — Jinja2. Every page `{% extends "base.html" %}`. `base.html` provides the navbar, footer, global CSS/JS includes, and blocks: `title`, `head`, `content`, `scripts`. Implemented pages: `landing`, `login`, `register`, `terms`, `privacy`.

**Frontend conventions:**

- `static/css/style.css` is a hand-written design system driven by CSS custom properties in `:root` (`--ink-*`, `--paper-*`, `--accent*`, `--radius-*`, `--font-display` = DM Serif Display, `--font-body` = DM Sans). Reuse these tokens rather than hardcoding colors/spacing.
- Auth pages share markup structure: `.auth-section` > `.auth-container` > `.auth-header` + `.auth-card` (form) + `.auth-switch`. Forms `POST` to their own path and render an `{{ error }}` string into `.auth-error` when present.
- Page-specific CSS goes inline in `{% block head %}` with a page-scoped class prefix (e.g. the landing page's video modal uses `.howto-*`). `static/js/main.js` is the single shared script and is currently empty.
- User-facing copy is India-oriented ("Track every rupee").
