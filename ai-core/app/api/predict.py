from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas import VitalSignsInput, HealthRiskResponse
from app.services.onnx_predictor import onnx_service

router = APIRouter(prefix="/predict", tags=["Physiological Prediction Engine"])


@router.post("/health-risk", response_model=HealthRiskResponse)
async def predict_health_risk(vitals: VitalSignsInput):
    """
    Sub-module B: Predicts disease condition and early warning timeline
    from time-series collar/bolus/ear-tag sensor data using ONNX surrogate model.
    """
    try:
        response = onnx_service.predict(vitals)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")


@router.post("/health-risk/batch", response_model=List[HealthRiskResponse])
async def predict_health_risk_batch(batch: List[VitalSignsInput]):
    """
    Batch inference endpoint for herd-level analysis across whole sheds.
    """
    results = []
    for item in batch:
        results.append(onnx_service.predict(item))
    return results
