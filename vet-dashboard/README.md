# PashuRakshak Veterinary & Official Command Center

Centralized web-based command center for district veterinary officers and animal husbandry departments (Govt. of Maharashtra).

## Key Features
1. **Interactive GIS Outbreak Map (Leaflet):** Real-time spatial tracking of early-warning disease clusters across Maharashtra districts (Pune, Ahmednagar, Kolhapur, Solapur, Nashik, Satara).
2. **Vaccination Coverage Overlay:** Toggleable heat layer correlating blocks with low vaccination coverage (<70%) against emerging disease clusters.
3. **Sortable Triage Queue (Red/Orange/Yellow):** Automated sorting of flagged livestock cases based on ONNX predictive risk probabilities.
4. **Field Vet Dispatching & Quarantine Orders:** One-click officer actions with dispatch confirmation and GPS coordinates routing.

## How to Run Locally

Open `index.html` in any browser or serve via:
```bash
python -m http.server 4000 --directory .
```
Open `http://localhost:4000` in your browser.
