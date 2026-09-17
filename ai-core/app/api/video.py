import os
import shutil
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas import VideoStreamRequest, VideoAnalysisResponse
from app.services.video_analytics import video_service

router = APIRouter(prefix="/analyze", tags=["Computer Vision Behavioral Video Pipeline"])


@router.post("/video", response_model=VideoAnalysisResponse)
async def analyze_uploaded_video(file: UploadFile = File(...)):
    """
    Sub-module A: Ingests an uploaded video clip (mp4, avi, mov) and detects behavioral anomalies:
    prolonged lying down, isolation from herd, and limping/abnormal gait.
    """
    suffix = os.path.splitext(file.filename)[1] or ".mp4"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp_path = tmp.name
        shutil.copyfileobj(file.file, tmp)

    try:
        result = video_service.analyze_video_file(tmp_path)
        result.source = file.filename
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video analysis failed: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@router.post("/stream", response_model=VideoAnalysisResponse)
async def analyze_stream(req: VideoStreamRequest):
    """
    Sub-module A: Ingests an RTSP / HTTP camera feed URL from existing farm CCTV infrastructure
    and samples frames asynchronously.
    """
    try:
        # In a real farm setting, opens RTSP stream; in demo environment, uses synthesized farm feed
        result = video_service.generate_mock_demo_analysis(source_name=req.stream_url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stream ingestion error: {str(e)}")
