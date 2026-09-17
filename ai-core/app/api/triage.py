from fastapi import APIRouter, HTTPException
from app.schemas import SymptomTriageRequest, SymptomTriageResponse
from app.services.symptom_triage import triage_service

router = APIRouter(prefix="/triage", tags=["Multilingual Rural Symptom Triage"])


@router.post("/symptom-text", response_model=SymptomTriageResponse)
async def triage_symptom_text(req: SymptomTriageRequest):
    """
    Sub-module C: Multilingual rule & NLP classifier mapping farmer-described symptoms
    (मराठी, हिन्दी, English) to probable disease shortlists with urgency score and immediate first-aid protocols.
    """
    try:
        result = triage_service.triage_symptoms(req)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Triage error: {str(e)}")
