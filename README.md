# decoda-deepshield

DeepShield is an AI-driven forensic security MVP for detecting deepfake-enabled financial fraud, KYC bypass, and synthetic identity attacks.

## Project structure

- `apps/web` – placeholder for future frontend
- `services/api` – FastAPI backend MVP
- `services/detection` – placeholder for future model services
- `docs` – architecture and scope docs
- `demo` – sample walkthrough assets

## Local development (API + web)

1. Copy environment variables:

   ```bash
   cp .env.example .env
   ```

2. Set values in `.env`:
   - `DATABASE_URL`:
     - Leave unset/empty for local SQLite default behavior (`services/api/deepshield.db`).
     - Set a Postgres URL for shared/dev cloud DBs (for example Railway Postgres).
   - `NEXT_PUBLIC_API_BASE_URL`:
     - For local frontend development, set `http://localhost:8000`.

3. Start API:

   ```bash
   cd services/api
   python -m venv .venv
   source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python -m app.main
   ```

4. Start web app (new terminal):

   ```bash
   cd apps/web
   npm install
   npm run dev
   ```

## First run (schema initialization)

Run this once for a new database, or whenever you need to initialize schema tables in an empty DB:

```bash
cd services/api
python -m app.db.bootstrap
```

This creates the SQLAlchemy model tables used by the API. With a database configured, records are persisted and survive browser refreshes and backend restarts.

## Database configuration

### Local default: SQLite

- If `DATABASE_URL` is not provided, the API defaults to a local SQLite database file.
- Data remains persisted in that DB file between app restarts until you delete the file.

### Railway Postgres

For Railway deployment (or local usage against Railway Postgres), set:

- `DATABASE_URL=postgresql://...` (Railway-provided connection string)

Then run schema initialization:

```bash
cd services/api
python -m app.db.bootstrap
```

With Postgres configured, data persistence survives API process restarts and deployment restarts because records are stored in the external database.

## Railway deployment settings (API)

- Service root: `services/api`
- Start command: `python -m app.main`
- Health endpoint: `GET /health`
- Runtime networking: binds `0.0.0.0` on `$PORT`
- Required env var: `DATABASE_URL` (Railway Postgres URL)

## Vercel deployment settings (frontend)

- Root Directory: `apps/web`
- Environment variable:
  - `NEXT_PUBLIC_API_BASE_URL=https://decoda-deepshield-production.up.railway.app`

This must point to your deployed API base URL so frontend requests are routed to the backend correctly.

## Live API smoke test (Windows CMD)

```cmd
curl -X GET "https://decoda-deepshield-production.up.railway.app/health"
curl -X GET "https://decoda-deepshield-production.up.railway.app/alerts"
curl -X GET "https://decoda-deepshield-production.up.railway.app/incidents"
```

For full Railway smoke test commands including analyze/export calls, see `services/api/README.md`.

### Core endpoints

- `GET /health`
- `POST /evidence/upload`
- `POST /detections/analyze`
- `GET /alerts`
- `GET /incidents`
- `GET /evidence/{evidence_id}/export`

## MVP disclaimer

DeepShield MVP is decision-support only and uses deterministic simulated detection logic. It does not provide real biometric identification, face recognition identity matching, paid API integrations, or production fraud adjudication.
