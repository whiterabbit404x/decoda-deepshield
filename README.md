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
uvicorn app.main:app --reload --port 8000
```

### Core endpoints

- `GET /health`
- `POST /evidence/upload`
- `POST /detections/analyze`
- `GET /alerts`
- `GET /incidents`
- `GET /evidence/{evidence_id}/export`

## Disclaimer

DeepShield MVP is decision-support only and uses deterministic simulated detection logic. It does not provide real biometric identification, paid API integrations, or production fraud adjudication.
