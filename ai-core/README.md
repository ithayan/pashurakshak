# PashuRakshak AI Core API ("The Brain")

FastAPI microservice executing computer vision analytics, ONNX surrogate inference, and multilingual symptom triage for livestock disease surveillance in Maharashtra.

## Key Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service health, ONNX runtime status, telemetry |
| `POST` | `/predict/health-risk` | ONNX surrogate disease prediction from ear-tag/bolus vitals |
| `POST` | `/predict/health-risk/batch` | Herd-wide batch inference |
| `POST` | `/analyze/video` | Video upload analysis (limping gait, prolonged lying, isolation) |
| `POST` | `/analyze/stream` | CCTV / RTSP camera feed stream ingestion |
| `POST` | `/triage/symptom-text` | Multilingual NLP triage with Marathi first-aid guidance |

## Quick Start

```bash
# From ai-core directory
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive OpenAPI documentation available at `http://localhost:8000/docs`.
