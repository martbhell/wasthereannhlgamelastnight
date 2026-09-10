# Agent Instructions & Guidelines for WTANGY

This repository is being rewritten from a Google App Engine (Python Flask + Google Cloud Storage) application to a **static site hosted on Cloudflare Pages**, powered by a Python static generator (`build.py`) and a daily scheduled rebuild job via GitHub Actions.

## Project Goal
Migrate the dynamic App Engine backend to a pre-rendered static site generator that produces all HTML pages, CSS assets, JSON data endpoints, RSS feeds, and OpenAPI Swagger documentation into a `dist/` directory. Provide a seamless local developer experience (`python build.py --serve`), deploy `dist/` to Cloudflare Pages, and set up a daily GitHub Actions workflow to rebuild and deploy updated NHL schedule data automatically.

---

## Target Architecture

### 1. Static Site Generator (`build.py`)
Replaces Flask dynamic routes by fetching data at build time and writing static outputs to `dist/`:
- **`dist/index.html`**: Default root page with client-side schedule evaluation.
- **`dist/<TEAM>/index.html`**: Pre-rendered team pages for all 32 NHL teams and abbreviations (DET, NYR, Boston Bruins, etc.).
- **`dist/menu/index.html`**: Interactive team selection menu.
- **`dist/docs/index.html` & `dist/openapi.json`**: OpenAPI 3.0 specification and interactive Swagger UI documentation for all public endpoints.
- **`dist/css/menu_team.css`**: Dynamic team color CSS generated from team definitions.
- **`dist/get_schedule` / `dist/get_schedule.json`**: Static JSON file containing the parsed schedule dictionary (`teamdates`).
- **`dist/version` / `dist/version.json`**: Static JSON file containing build timestamp ISO date.
- **`dist/atom.xml`**: Static RSS/Atom feed of schedule updates.
- **`dist/static/`**: Copy of static assets (fonts, favicons, app.css, client scripts).

### 2. Local Developer Experience (DX)
- **`python build.py --serve [port]`**: Generates the static site and launches a local HTTP server (default port `8080`) for rapid local iteration and testing.
- **`python build.py --watch`**: Optionally re-builds on file changes during local development.

### 3. Client-Side Dynamics (`src/static/preferences.js` & `colorpreferences.js`)
- Preserves `localStorage` functionality for team and background color preferences.
- Evaluates YES/NO queries client-side using `schedule.json` for dynamic date queries (`/$DATE`, `/$TEAM/$DATE`) or fallback SPA routing.

### 4. Cloudflare Pages Configuration (`dist/_redirects`, `dist/_headers`)
- Handles clean route aliases (e.g. `/get_schedule` -> `/get_schedule.json`, `/version` -> `/version.json`, `/docs` -> `/docs/index.html`).
- Configures caching and MIME headers.

### 5. Daily Schedule Rebuild Job (`.github/workflows/deploy.yml`)
- Scheduled workflow running daily (`cron: '0 6 * * *'`) and on `push` to `main`.
- Runs `python build.py`, validates via `e2e_test.py`, and deploys `dist/` to Cloudflare Pages via `cloudflare/pages-action` or `wrangler`.

---

## Instructions for AI Agents

### Chunked Execution Protocol
To avoid running into rate limits or large context limits:
1. **Consult `ROADMAP.md`**: Identify the next pending chunk (marked `[ ]`).
2. **Execute Chunk**: Make the exact minimal file changes required for that chunk.
3. **Verify Chunk**: Run local build (`python build.py`) and test commands.
4. **Update `ROADMAP.md`**: Mark the completed chunk as `[x]`.
5. **Summarize Progress**: Provide a brief update to the user with the next recommended step.

### Quality & Compatibility Requirements
- Preserve all existing public endpoints (`/$TEAM`, `/$DATE`, `/$TEAM/$DATE`, `/menu`, `/version`, `/get_schedule`, `/atom.xml`, `?JSON` parameter, `/docs`).
- Preserve CLI User-Agent plain-text support (`curl`, `wget`, `python-urllib`).
- Preserve `e2e_test.py` compatibility.
- Ensure clean code formatting (`black`, `isort`, `pylint`).

---

## Quick Reference Commands

```bash
# Build static site to dist/
python build.py

# Launch local dev server (Builds static site and serves at http://localhost:8080)
python build.py --serve

# Run E2E test suite against local build
python e2e_test.py --host http://localhost:8080

# Code linting & formatting
black --check build.py src/*.py *.py
isort --check build.py src/*.py *.py
pylint --rcfile=pylintrc build.py src/*.py *.py
```
