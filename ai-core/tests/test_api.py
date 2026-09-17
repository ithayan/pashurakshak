import os
import sys

# Add app to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def run_all_tests():
    print("==================================================")
    print("Running PashuRakshak AI Core Test Suite")
    print("==================================================")
    passed = 0
    total = 0

    def assert_test(name, condition, details=""):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"  [PASS] {name}")
        else:
            print(f"  [FAIL] {name}: {details}")

    # 1. Health endpoint
    try:
        r = client.get("/health")
        d = r.json()
        assert_test("Health check endpoint", r.status_code == 200 and d["status"] == "HEALTHY")
    except Exception as e:
        assert_test("Health check endpoint", False, str(e))

    # 2. Healthy animal prediction
    try:
        payload = {
            "animal_id": "MAH-PUN-001",
            "temperature": 38.5,
            "temp_24h_delta": 0.05,
            "temp_24h_mean": 38.5,
            "rumination_minutes": 460.0,
            "rumination_drop_pct": 0.0,
            "feeding_minutes": 260.0,
            "feeding_drop_pct": 0.0,
            "activity_index": 100.0,
            "activity_drop_pct": 0.0,
            "language": "mr"
        }
        r = client.post("/predict/health-risk", json=payload)
        d = r.json()
        assert_test(
            "ONNX prediction - Healthy cattle",
            r.status_code == 200 and d["risk_level"] in ["LOW", "MEDIUM"]
        )
    except Exception as e:
        assert_test("ONNX prediction - Healthy cattle", False, str(e))

    # 3. Diseased animal prediction (Mastitis early signal)
    try:
        payload = {
            "animal_id": "MAH-AHM-042",
            "temperature": 39.7,
            "temp_24h_delta": 1.1,
            "temp_24h_mean": 39.4,
            "rumination_minutes": 290.0,
            "rumination_drop_pct": 37.0,
            "feeding_minutes": 180.0,
            "feeding_drop_pct": 30.0,
            "activity_index": 72.0,
            "activity_drop_pct": 28.0,
            "language": "mr"
        }
        r = client.post("/predict/health-risk", json=payload)
        d = r.json()
        assert_test(
            "ONNX prediction - Elevated mastitis risk",
            r.status_code == 200 and d["risk_level"] in ["HIGH", "MEDIUM"] and len(d["recommended_action"]) > 10
        )
    except Exception as e:
        assert_test("ONNX prediction - Elevated mastitis risk", False, str(e))

    # 4. Marathi symptom triage (Mastitis / कासदाह)
    try:
        payload = {
            "query_text": "कास गरम झाली आहे आणि दूध खूप कमी झाले, दुधात गुठळ्या दिसत आहेत",
            "language": "mr"
        }
        r = client.post("/triage/symptom-text", json=payload)
        d = r.json()
        is_mastitis = "कासदाह" in d["primary_condition_mr"] or "Mastitis" in d["primary_condition"]
        assert_test(
            "Marathi Symptom Triage - Mastitis (कासदाह)",
            r.status_code == 200 and is_mastitis and d["urgency_level"] == "CRITICAL"
        )
    except Exception as e:
        assert_test("Marathi Symptom Triage - Mastitis (कासदाह)", False, str(e))

    # 5. Marathi symptom triage (FMD / लाळ्या खुरकूत)
    try:
        payload = {
            "query_text": "गाय चालताना लंगडत आहे आणि तोंडातून सारखी लाळ गळते, तोंडात फोड आले आहेत",
            "language": "mr"
        }
        r = client.post("/triage/symptom-text", json=payload)
        d = r.json()
        is_fmd = "लाळ्या खुरकूत" in d["primary_condition_mr"] or "Foot-and-Mouth" in d["primary_condition"]
        assert_test(
            "Marathi Symptom Triage - FMD (लाळ्या खुरकूत)",
            r.status_code == 200 and is_fmd and d["urgency_level"] == "CRITICAL"
        )
    except Exception as e:
        assert_test("Marathi Symptom Triage - FMD (लाळ्या खुरकूत)", False, str(e))

    # 6. Stream video analytics
    try:
        payload = {
            "stream_url": "rtsp://pune-dairy-pen-camera-01.local/live",
            "sampling_fps": 1.0,
            "stream_duration_sec": 5
        }
        r = client.post("/analyze/stream", json=payload)
        d = r.json()
        assert_test(
            "Stream video behavioral analytics",
            r.status_code == 200 and d["total_animals_detected"] > 0 and len(d["anomalies_detected"]) > 0
        )
    except Exception as e:
        assert_test("Stream video behavioral analytics", False, str(e))

    print("--------------------------------------------------")
    print(f"Result: {passed}/{total} tests passed ({int(passed/total*100)}%)")
    print("==================================================")
    if passed < total:
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
