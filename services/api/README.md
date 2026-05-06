# DeepShield API (MVP)

Decision-support backend for simulated synthetic fraud detection.

## Run locally

```bash
cd services/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Test

```bash
cd services/api
pytest -q
```

## Disclaimer

This MVP provides deterministic, simulated risk scoring for investigation support only. It is **not** a production biometric verification system and should not be used as a sole decision-maker.
