# decoda-deepshield

DeepShield is an AI-driven forensic security MVP for detecting deepfake-enabled financial fraud, KYC bypass, and synthetic identity attacks.

## Project structure

- `apps/web` – placeholder for future frontend
- `services/api` – FastAPI backend MVP
- `services/detection` – placeholder for future model services
- `docs` – architecture and scope docs
- `demo` – sample walkthrough assets

## Backend quickstart

See `services/api/README.md` for full instructions.

```bash
cd services/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

## Railway deployment settings

- Service root: `services/api`
- Start command: `python -m app.main`
- Health endpoint: `GET /health`
- Runtime networking: binds `0.0.0.0` on `$PORT`

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
