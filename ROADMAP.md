# WTANGY Cloudflare Pages Migration Roadmap

This roadmap details the step-by-step migration of **Was There An NHL Game Yesterday? (WTANGY)** from Google App Engine to a Static Site hosted on Cloudflare Pages with daily automated GitHub Actions rebuilds, OpenAPI Swagger documentation (`/docs`), and an enhanced local developer experience.

Each chunk is designed to be self-contained, testable, and executable in a single agent turn without exceeding API rate limits or context windows.

---

## Phase 1: Static Builder Core (`build.py`) & Data Pipeline
- [x] **Chunk 1.1: Build Script Foundation, Dev Server & Schedule Fetcher**
  - Create `build.py`.
  - Add `--serve` CLI flag for local developer experience (DX) that runs an HTTP server at `http://localhost:8080` serving `dist/`.
  - Import schedule parsing logic from `src/nhlhelpers.py` and `src/main.py`.
  - Fetch schedule data from NHL API (`https://api-web.nhle.com/v1/schedule/now` + 4 weeks ahead).
  - Generate `dist/get_schedule` (JSON) and `dist/version` (JSON).

- [ ] **Chunk 1.2: Atom Feed Static Generator**
  - Port `atom_feed_manager` logic into `build.py`.
  - Compare schedule changes against previous build/state.
  - Output `dist/atom.xml` with Atom 1.0 feed entries.

- [ ] **Chunk 1.3: Static Team CSS Generator**
  - Port `menu_css` route logic into `build.py`.
  - Generate `dist/css/menu_team.css` using team definitions and HSL/Hex color contrast rules.

- [ ] **Chunk 1.4: OpenAPI Specification & Swagger UI (`/docs`) Generator**
  - Create OpenAPI 3.0 schema generator in `build.py` outputting `dist/openapi.json`.
  - Generate interactive Swagger UI documentation at `dist/docs/index.html`.
  - Document all endpoints (`/get_schedule`, `/version`, `/atom.xml`, `/$TEAM`, `/$DATE`, `/$TEAM/$DATE`, `?JSON`, `/menu`).

---

## Phase 2: Static HTML Generation & Client-Side Engine
- [ ] **Chunk 2.1: Template & Static Asset Pipeline**
  - Refactor HTML templates (`src/templates/`) for static rendering (Jinja2 standalone).
  - Copy static assets (`src/static/` fonts, favicons, app.css, JS) to `dist/`.

- [ ] **Chunk 2.2: Pre-rendered HTML Page Generation**
  - Pre-render `dist/index.html` (root page).
  - Pre-render `dist/menu/index.html` (interactive team picker).
  - Pre-render static pages for all 32 NHL teams and abbreviations (`dist/<TEAM>/index.html`, e.g., `dist/DET/index.html`, `dist/RedWings/index.html`).

- [ ] **Chunk 2.3: Dynamic Client-Side JS & CLI Support**
  - Enhance client-side scripts (`src/static/preferences.js`, `colorpreferences.js`, `app.js`) to evaluate dynamic date URLs (`/$DATE`, `/$TEAM/$DATE`) directly in browser JS using `get_schedule.json`.
  - Maintain CLI User-Agent plain-text `YES`/`NO` responses (`curl`, `wget`).

- [ ] **Chunk 2.4: Cloudflare Pages Configuration**
  - Generate `dist/_redirects` for clean URLs, route fallbacks (`/docs` -> `/docs/index.html`), and alias rewrites.
  - Generate `dist/_headers` for proper MIME types and caching rules.

---

## Phase 3: Testing & Code Quality Suite
- [ ] **Chunk 3.1: Adapt E2E Test Suite for Static Server & Dev Server**
  - Update `e2e_test.py` to start and test against `python build.py --serve` or `python -m http.server -d dist 8080`.
  - Ensure all endpoint assertions (`/`, `/$TEAM`, `/$DATE`, `/get_schedule`, `/version`, `/atom.xml`, `/css/menu_team.css`, `/docs`) pass.

- [ ] **Chunk 3.2: Code Clean-up & Linting**
  - Remove GAE-specific code (`google-cloud-storage` imports, GAE environment variables, `app.yaml`, `cron.yaml`).
  - Configure `black`, `isort`, `pylint` for `build.py` and updated Python modules.

---

## Phase 4: CI/CD Rebuild & Cloudflare Pages Deployment
- [ ] **Chunk 4.1: GitHub Actions Daily Rebuild Workflow**
  - Create `.github/workflows/deploy.yml`.
  - Configure daily cron trigger (`cron: '0 6 * * *'`) + push/PR triggers.
  - Add build (`python build.py`), test (`python e2e_test.py`), and Cloudflare Pages deployment steps (`cloudflare/pages-action`).

- [ ] **Chunk 4.2: Documentation & Cleanup**
  - Remove legacy GAE workflow (`.github/workflows/pythonapp.yml`) and GAE docs (`gcloud.md`).
  - Update `README.md` with Cloudflare Pages architecture overview, DX dev server instructions (`python build.py --serve`), Swagger docs overview, and deployment guide.

---

## Progress Summary
- **Total Chunks**: 12
- **Completed**: 1
- **Remaining**: 11
