# PashuRakshak Farmer App ("The UI")

Lightweight, mobile-first Progressive Web App (PWA) designed for dairy farmers in rural Maharashtra.

## Key Design Principles
1. **Low-Bandwidth Operation:** Zero video streaming to the farmer's phone. Only lightweight telemetry and actionable guidance are sent, ensuring instant loading even on 2G/3G cellular networks.
2. **Marathi-First Multilingual Support:** Instant language toggle between **मराठी (Marathi)**, हिन्दी (Hindi), and English.
3. **Early Warning Risk Cards:** Displays pre-clinical lead times (e.g. *"Cow #42 — 88% probability of early-stage mastitis 2.5 days before clinical signs"*).
4. **Biomarker Trend Charts:** Interactive pure-SVG charts plotting body temperature, rumination, feeding, and activity curves without heavy external charting libraries.
5. **AI Symptom Reporter:** Voice recording and native text input feeding into the AI Core triage engine with audio playback of medical advice in Marathi.

## How to Run Locally

Open `index.html` in any web browser or serve via any static HTTP server:
```bash
# Using Python built-in server
python -m http.server 3000 --directory .
```
Open `http://localhost:3000` in your browser.
