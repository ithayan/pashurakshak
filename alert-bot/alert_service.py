"""
PashuRakshak Alert Bot - Notification Dispatch Service
======================================================
Coordinates threshold triggers from AI Core to format localized WhatsApp messages
and IVR prompts for rural dairy farmers in Maharashtra.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Optional

# Ensure UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from twilio_client import twilio_client

logger = logging.getLogger("pashurakshak.alerts")
TEMPLATES_PATH = os.path.join(os.path.dirname(__file__), "templates", "alerts.json")


class AlertService:
    def __init__(self):
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, Any]:
        if os.path.exists(TEMPLATES_PATH):
            with open(TEMPLATES_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def dispatch_health_alert(
        self,
        animal_id: str,
        condition_code: str,
        probability: float,
        lead_days: float,
        temperature: float,
        rumination_drop_pct: float,
        farmer_phone: str = "+919822012345",
        language: str = "mr"
    ) -> Dict[str, Any]:
        """
        Formats and dispatches disease risk alert in farmer's preferred language (defaults to Marathi).
        """
        template_key = condition_code.upper() if condition_code.upper() in self.templates else "MASTITIS"
        template_group = self.templates.get(template_key, self.templates.get("MASTITIS", {}))
        template_text = template_group.get(language, template_group.get("mr", ""))

        message_body = template_text.format(
            tag_id=animal_id,
            probability=int(probability * 100),
            lead_days=round(lead_days, 1),
            temp=round(temperature, 1),
            rum_drop=round(rumination_drop_pct, 1)
        )

        metadata = {
            "type": "PHYSIOLOGICAL_HEALTH_ALERT",
            "animal_id": animal_id,
            "condition": condition_code,
            "probability": probability,
            "language": language
        }

        return twilio_client.send_whatsapp_message(farmer_phone, message_body, metadata)

    def dispatch_behavioral_alert(
        self,
        animal_id: str,
        anomaly_type: str,
        anomaly_title_mr: str,
        confidence: float,
        timestamp: str,
        farmer_phone: str = "+919822012345",
        language: str = "mr"
    ) -> Dict[str, Any]:
        """
        Formats and dispatches camera behavioral anomaly alert.
        """
        template_group = self.templates.get("BEHAVIORAL_ANOMALY", {})
        template_text = template_group.get(language, template_group.get("mr", ""))

        message_body = template_text.format(
            tag_id=animal_id,
            anomaly_title_mr=anomaly_title_mr,
            anomaly_title_hi=anomaly_title_mr,
            anomaly_title_en=anomaly_type,
            confidence=int(confidence * 100),
            timestamp=timestamp
        )

        metadata = {
            "type": "CCTV_BEHAVIORAL_ALERT",
            "animal_id": animal_id,
            "anomaly_type": anomaly_type,
            "confidence": confidence,
            "language": language
        }

        return twilio_client.send_whatsapp_message(farmer_phone, message_body, metadata)


# Global singleton instance
alert_service = AlertService()


if __name__ == "__main__":
    print("Testing Marathi WhatsApp alert dispatch...")
    res = alert_service.dispatch_health_alert(
        animal_id="MAH-PUN-TAG-1042",
        condition_code="MASTITIS",
        probability=0.88,
        lead_days=2.5,
        temperature=39.6,
        rumination_drop_pct=34.5,
        language="mr"
    )
    print("Dispatched result:", json.dumps(res, indent=2, ensure_ascii=False))
