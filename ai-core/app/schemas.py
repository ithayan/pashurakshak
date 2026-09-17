from typing import Dict, List, Optional
from pydantic import BaseModel, Field


# -------------------------------------------------------------
# Sub-module B: Physiological Prediction Schemas
# -------------------------------------------------------------

class VitalSignsInput(BaseModel):
    animal_id: str = Field(..., example="MAH-PUN-TAG-1042")
    temperature: float = Field(..., description="Current body temperature in °C", example=39.4)
    temp_24h_delta: Optional[float] = Field(None, description="24h temperature change (°C)", example=0.8)
    temp_24h_mean: Optional[float] = Field(None, description="24h mean temperature (°C)", example=39.1)
    rumination_minutes: float = Field(..., description="Rumination minutes in last 24h", example=310.0)
    rumination_drop_pct: Optional[float] = Field(None, description="Percentage drop vs baseline", example=31.2)
    feeding_minutes: float = Field(..., description="Feeding minutes in last 24h", example=185.0)
    feeding_drop_pct: Optional[float] = Field(None, description="Percentage drop vs baseline", example=28.5)
    activity_index: float = Field(..., description="Locomotion/activity index", example=74.0)
    activity_drop_pct: Optional[float] = Field(None, description="Percentage drop vs baseline", example=26.0)
    language: Optional[str] = Field("mr", description="Response language: 'mr' (Marathi), 'hi' (Hindi), 'en' (English)")


class HealthRiskResponse(BaseModel):
    animal_id: str
    risk_level: str = Field(..., description="HIGH, MEDIUM, or LOW")
    disease_probability: float = Field(..., description="Confidence probability of likely condition [0.0 - 1.0]")
    likely_condition: str = Field(..., description="Diagnosed condition with Marathi / Hindi translation")
    condition_code: str = Field(..., description="Healthy, Mastitis, FMD, LSD, BRD, Ketosis")
    days_to_symptom_estimate: float = Field(..., description="Estimated days before overt clinical presentation")
    is_early_warning: bool = Field(..., description="True if detected in pre-clinical/subclinical window")
    recommended_action: str = Field(..., description="Actionable advice in requested language")
    detailed_probabilities: Dict[str, float]
    dispatch_whatsapp_alert: bool = Field(False, description="True if risk exceeds alert threshold")


# -------------------------------------------------------------
# Sub-module A: Video Analytics Schemas
# -------------------------------------------------------------

class VideoStreamRequest(BaseModel):
    stream_url: str = Field(..., description="RTSP URL or video source path", example="rtsp://demo-farm-camera.local/stream1")
    sampling_fps: Optional[float] = Field(1.0, description="Sampling rate in frames per second")
    stream_duration_sec: Optional[int] = Field(10, description="Sampling window in seconds")


class AnomalyItem(BaseModel):
    anomaly_type: str = Field(..., description="PROLONGED_LYING, HERD_ISOLATION, LIMPING_GAIT, or NORMAL")
    anomaly_title_mr: str = Field(..., description="Marathi name of anomaly")
    confidence: float
    bbox: List[int] = Field(..., description="[x1, y1, x2, y2] bounding box coordinates")
    severity: str = Field(..., description="CRITICAL, WARNING, or NORMAL")
    description: str


class VideoAnalysisResponse(BaseModel):
    source: str
    total_animals_detected: int
    anomalies_detected: List[AnomalyItem]
    overall_status: str
    timestamp: str
    frame_snapshot_base64: Optional[str] = None


# -------------------------------------------------------------
# Sub-module C: Symptom Triage Schemas
# -------------------------------------------------------------

class SymptomTriageRequest(BaseModel):
    query_text: str = Field(..., description="Farmer described symptoms in Marathi, Hindi, or English", example="कास गरम आहे आणि दूध कमी झाले आहे, गाय बसून राहते")
    language: Optional[str] = Field("mr", description="'mr' (Marathi), 'hi' (Hindi), 'en' (English)")


class ConditionMatch(BaseModel):
    condition_name: str
    condition_name_mr: str
    probability: float
    key_indicators: List[str]


class SymptomTriageResponse(BaseModel):
    input_query: str
    detected_language: str
    primary_condition: str
    primary_condition_mr: str
    urgency_level: str = Field(..., description="CRITICAL, MODERATE, or ROUTINE")
    probable_conditions: List[ConditionMatch]
    immediate_farmer_actions: List[str]
    marathi_audio_prompt_text: str
    nearest_dispensary_advice: str
