# PashuRakshak Rural Alert Layer (WhatsApp & IVR Bot)

Automated notification layer delivering real-time, low-bandwidth early warning alerts to dairy farmers across rural Maharashtra in Marathi (मराठी), Hindi, and English.

## Features
- **Twilio WhatsApp Business API integration** with live production and sandbox fallback.
- **Marathi-First Templates (`templates/alerts.json`):** Empathetic, actionable alerts with lead time (e.g. "लक्षणे दिसण्याच्या २.५ दिवस आधी पूर्वसूचना"), temperature, rumination drop, and 1962 helpline.
- **Persistent Alert History (`alerts_history.json`):** Tracks all dispatched alerts with timestamps, delivery status, and payload.
- **Twilio Studio IVR Flow (`ivr/twilio_studio_flow.json`):** Interactive voice call script in Marathi for non-smartphone farmers with keypad routing (Press 1 for first aid, Press 2 for Govt 1962 hotline).

## Usage
```bash
# Test Marathi WhatsApp alert dispatch
python alert_service.py
```
