# PashuRakshak (पशुरक्षक)
### AI-Powered Livestock Health Surveillance & Early-Warning Platform
**Smart India Hackathon (SIH) — Govt. of Maharashtra (Category: Software)**

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128-green.svg)](https://fastapi.tiangolo.com/)
[![ONNX Runtime](https://img.shields.io/badge/ONNX-Runtime-blueviolet.svg)](https://onnxruntime.ai/)
[![Language](https://img.shields.io/badge/Language-Marathi%20%7C%20Hindi%20%7C%20English-orange.svg)](#)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](#)

---

## 🐄 Mission & Architecture

**PashuRakshak** is a pure-software, cloud-first livestock health surveillance platform that ingests data from **existing off-the-shelf farm infrastructure** (CCTV/IP cameras via RTSP or uploaded video files, commercial ear-tag/bolus APIs, and veterinary clinical logs) with **zero custom microcontrollers or hardware**.

It couples real-time computer vision behavioral tracking with an ONNX surrogate neural network trained on a physiologically-grounded Digital Twin simulator to detect bovine diseases (Mastitis, FMD, LSD, BRD, Ketosis) **48 to 72 hours before overt clinical signs appear**.

```
pashurakshak/
├── ai-core/            # FastAPI microservice: ONNX predictor, YOLO vision pipeline, Marathi symptom triage
├── digital-twin/       # Compartmental physiological disease simulator & ONNX surrogate model generator
├── farmer-app/         # Low-bandwidth rural PWA (Marathi default, SVG vitals charts, voice/photo triage)
├── vet-dashboard/      # Maharashtra GIS outbreak command center (Leaflet heatmaps, vaccination overlays)
├── alert-bot/          # WhatsApp Business API dispatcher & Twilio IVR voice flow
├── demo/               # 24 simulated cattle profiles, sample video fixtures & master CLI demo script
├── docker-compose.yml  # Monorepo container orchestration
└── PITCH_NOTES.md      # SIH judges pitch deck notes & technical defenses
```

---

## ⚡ Quick Start

### 1. Run AI Core Backend
```bash
cd ai-core
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive OpenAPI documentation: `http://localhost:8000/docs`

### 2. Run Automated Test Suite
```bash
cd ai-core
python tests/test_api.py
```

### 3. Launch Farmer PWA (Low-Bandwidth Mobile Interface)
```bash
cd farmer-app
python -m http.server 3000
```
Open `http://localhost:3000` on any mobile or desktop browser.

### 4. Launch Veterinary GIS Command Center
```bash
cd vet-dashboard
python -m http.server 4000
```
Open `http://localhost:4000` to inspect Maharashtra district outbreak clusters and alert queues.

### 5. Run the Master End-to-End Presentation Demo
```bash
cd demo
python run_e2e_demo.py
```

---

## 📜 SIH Compliance & Non-Negotiables
- **Zero Custom Hardware:** Runs on standard CCTV cameras (RTSP) and commercial tags.
- **No Proprietary Toolchain Dependencies:** Pure Python ODE simulator replaces MATLAB/Simulink; exports directly to portable ONNX.
- **Physiologically Derived Synthetic Data:** Modeled after peer-reviewed bovine pathophysiology (circadian temp, acute rumination drop, feeding depression).
- **Marathi-First Accessibility:** Built specifically for rural dairy farmers in Maharashtra with vernacular terminology, voice triage, audio playback, and WhatsApp alerts with 1962 hotline.
