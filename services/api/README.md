# DeepShield API (MVP)

Decision-support backend for simulated synthetic fraud detection.

## Local run

```bash
cd services/api
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.main
```

The app binds to `0.0.0.0` and uses `$PORT` (default `8000`) for Railway compatibility.

## Environment configuration

From repo root, create `.env` from `.env.example` and set:

- `DATABASE_URL`
  - Empty/unset for default local SQLite behavior.
  - Postgres URL for Railway or any hosted Postgres.
- `NEXT_PUBLIC_API_BASE_URL`
  - Used by frontend (Vercel/local web app) and should point at this API.

## First run (schema initialization)

This service currently uses SQLAlchemy metadata bootstrap (instead of Alembic) for initial schema creation.

```bash
cd services/api
python -m app.db.bootstrap
```

The command creates all model tables (Organization, User, Workspace, Evidence, Detection, Alert, Incident, AuditEvent) and constraints from `Base.metadata`.

With a configured database, records persist and survive browser refreshes and API process restarts.

## Database behavior

### SQLite default (local)

If `DATABASE_URL` is unset, the app uses local SQLite. Data is persisted in the SQLite DB file and remains after service restart unless the file is removed.

### Postgres (Railway)

Set `DATABASE_URL` to your Railway Postgres connection string, then initialize schema:

```bash
cd services/api
python -m app.db.bootstrap
```

Data is stored in Postgres and persists across Railway restarts/redeploys.

## Local full-stack startup (API + web)

1. Start API (this folder):

   ```bash
   cd services/api
   source .venv/bin/activate  # if already created
   python -m app.main
   ```

2. Start web in a second terminal:

   ```bash
   cd apps/web
   npm install
   npm run dev
   ```

3. Ensure frontend points to API with:
   - `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`

## Railway deployment settings

- Root directory: `services/api`
- Start command: `python -m app.main`
- Health check path: `/health`
- Environment variables:
  - `PORT` provided by Railway runtime
  - `DATABASE_URL` set to Railway Postgres URL

## Vercel frontend configuration

In Vercel (`apps/web`):

- Set `NEXT_PUBLIC_API_BASE_URL` to your API deployment URL (for example, Railway public URL).
- Redeploy frontend after changing the variable.

## Test

```bash
cd services/api
pytest -q
```

## Railway smoke test (Windows CMD)

```cmd
curl -X GET "https://decoda-deepshield-production.up.railway.app/health"

curl -X POST "https://decoda-deepshield-production.up.railway.app/detections/analyze" ^
  -H "Content-Type: application/json" ^
  -d "{\"evidence_id\":\"REPLACE_WITH_EVIDENCE_ID\"}"

curl -X GET "https://decoda-deepshield-production.up.railway.app/alerts"

curl -X GET "https://decoda-deepshield-production.up.railway.app/incidents"

curl -X GET "https://decoda-deepshield-production.up.railway.app/evidence/REPLACE_WITH_EVIDENCE_ID/export"
```

## MVP disclaimer

This MVP provides deterministic, simulated risk scoring for investigation support only. It does **not** include real biometric identification, face recognition identity matching, paid API integrations, or production fraud adjudication.
