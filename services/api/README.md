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

## Test

```bash
cd services/api
pytest -q
```

## Railway deployment settings

- Root directory: `services/api`
- Start command: `python -m app.main`
- Health check path: `/health`
- Environment variable: `PORT` provided by Railway runtime

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
