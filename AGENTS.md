# AGENTS.md

POS web app ("Tienda el Regalito") for a small Guatemala store. Spanish-language code, comments, and UI (currency is Q / quetzal, locale `es-GT`). Single repo with three parts: `backend/` (FastAPI), `frontend/` (static HTML/CSS/JS, no build step), `database/` (Postgres init SQL). No tests, lint, or CI config exists.

## Run

- Database (PostgreSQL 15 in Docker): `docker compose up -d`. Exposes **host port 5433**, not 5432.
- Backend: from `backend/` with the venv at repo root:
  - `..\venv\Scripts\python.exe -m uvicorn app.main:app --reload` (Windows), or activate `venv` and run `uvicorn app.main:app --reload`.
- Frontend has **no build step** and no `package.json`; `package-lock.json` is empty/vestigial. Bootstrap 5 is loaded from CDN.

## Architecture / gotchas

- `backend/app/main.py` mounts the `frontend/` dir at `/` via `StaticFiles(html=True)`. One server serves both UI and API, so the app must be opened via `http://localhost:8000`, not by opening `index.html` directly (frontend `app.js` uses relative `API_URL = '/api'`).
- API prefixes: `/api/auth`, `/api/caja`, `/api/productos`. Auth is OAuth2 password flow (JWT, HS256, `ACCESS_TOKEN_EXPIRE_MINUTES=480`).
- DB connection is read directly from env in `backend/app/db/database.py` (`load_dotenv()` + `os.getenv("DATABASE_URL")`, raises if missing) — it does **not** use `app/core/config.py` (pydantic-settings), so editing `config.py` will not change the connection. `backend/.env` is required and gitignored; its `DATABASE_URL` hardcodes `localhost:5433`.
- `backend/.env` contains a dev `SECRET_KEY`; it is gitignored but committed config in `config.py` uses a placeholder default. Do not reuse the placeholder key in production.
- Seeding: `database/init.sql` runs automatically only on **first** container start (empty `postgres_data` volume). It creates tables + `admin`/`admin123` (role `Admin`) + 3 seed products with barcodes `7501055300075`, `7501000123456`, `7501000987654`. To re-apply changes, run `docker compose down -v` then `up`.
- The two `init_db.py` scripts (repo root and `backend/app/db/`) are **broken and inconsistent**: the root one fails with `ModuleNotFoundError: No module named 'app'` (the `app` package lives under `backend/`), and both seed a product with `stock=` while the model/schema column is `current_stock` (would raise). Prefer `database/init.sql` for seeding.
- Model/schema column is `Product.current_stock` (model `backend/app/db/models.py`, schema `backend/app/schemas/schemas.py`); `database/init.sql` correctly uses `current_stock`.
- Frontend is mostly a mock shell: only login is wired to the API (`/api/auth/login`); the rest of the dashboard, register/recover/verify/reset flows, and KPI numbers are static placeholders.
