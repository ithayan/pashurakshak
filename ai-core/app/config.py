import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent

# Model Paths
ONNX_MODEL_PATH = os.getenv(
    "ONNX_MODEL_PATH",
    str(PROJECT_ROOT / "digital-twin" / "models" / "livestock_health_surrogate.onnx")
)
MODEL_METADATA_PATH = os.getenv(
    "MODEL_METADATA_PATH",
    str(PROJECT_ROOT / "digital-twin" / "models" / "model_metadata.json")
)

# Thresholds
HIGH_RISK_THRESHOLD = float(os.getenv("HIGH_RISK_THRESHOLD", "0.70"))
MEDIUM_RISK_THRESHOLD = float(os.getenv("MEDIUM_RISK_THRESHOLD", "0.40"))

# Default Language (emphasizing Marathi as requested)
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "mr")

# API Configuration
API_TITLE = "LaxmiAI (लक्ष्मीAI) Core API"
API_VERSION = "1.0.0"
API_DESCRIPTION = """
**LaxmiAI (लक्ष्मीAI)** - AI-Powered Livestock Health Surveillance Platform
SIH Problem Statement: Govt. of Maharashtra (Early detection, prevention & management of livestock diseases).

Features:
- **Sub-module A:** Computer Vision Behavioral Anomaly Detection (Isolation, Prolonged Lying, Limping Gait)
- **Sub-module B:** ONNX Multi-task Physiological Health Risk Predictor
- **Sub-module C:** Multilingual Rural Symptom Triage with Veterinary RAG (मराठी, हिन्दी, English)
"""
