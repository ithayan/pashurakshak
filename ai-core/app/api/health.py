from fastapi import APIRouter
from datetime import datetime
import onnxruntime as ort
from app.config import API_VERSION, ONNX_MODEL_PATH

router = APIRouter(tags=["Health & Telemetry"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint returning system status, ONNX runtime availability, and timestamp.
    """
    ort_available = True
    try:
        _ = ort.get_device()
    except Exception:
        ort_available = False

    return {
        "status": "HEALTHY",
        "service": "PashuRakshak AI Core API",
        "version": API_VERSION,
        "timestamp": datetime.now().isoformat(),
        "onnx_model_path": ONNX_MODEL_PATH,
        "onnx_runtime_active": ort_available,
        "supported_languages": ["mr (मराठी)", "hi (हिन्दी)", "en (English)"],
        "submodules": {
            "submodule_a_vision": "ACTIVE",
            "submodule_b_onnx_predictor": "ACTIVE",
            "submodule_c_triage": "ACTIVE"
        }
    }
