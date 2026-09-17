"""
PashuRakshak Alert Bot - Twilio WhatsApp Client & Sandbox Manager
================================================================
Dispatches real-time WhatsApp notifications to farmers in rural Maharashtra.
Supports both live Twilio WhatsApp Business API and an interactive local sandbox
with persistent alert history for hackathon demonstration.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger("pashurakshak.twilio")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
HISTORY_FILE = os.path.join(os.path.dirname(__file__), "alerts_history.json")


class TwilioWhatsAppClient:
    def __init__(self):
        self.is_live = bool(TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN)
        self.client = None
        if self.is_live:
            try:
                from twilio.rest import Client
                self.client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
                logger.info("Connected to live Twilio WhatsApp API")
            except Exception as e:
                logger.warning(f"Failed to initialize live Twilio client: {e}. Running in sandbox mode.")
                self.is_live = False
        else:
            logger.info("Twilio credentials not set. Running in PashuRakshak Sandbox Dispatcher mode.")

    def send_whatsapp_message(
        self,
        to_phone: str,
        message_body: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Dispatches a WhatsApp alert to farmer's mobile number.
        """
        timestamp = datetime.now().isoformat()
        clean_phone = to_phone if to_phone.startswith("whatsapp:") else f"whatsapp:{to_phone}"

        alert_record = {
            "id": f"ALT-{int(datetime.now().timestamp() * 1000)}",
            "to": clean_phone,
            "timestamp": timestamp,
            "body": message_body,
            "metadata": metadata or {},
            "status": "QUEUED"
        }

        if self.is_live and self.client:
            try:
                msg = self.client.messages.create(
                    from_=TWILIO_WHATSAPP_NUMBER,
                    to=clean_phone,
                    body=message_body
                )
                alert_record["status"] = "SENT_TWILIO"
                alert_record["twilio_sid"] = msg.sid
                logger.info(f"WhatsApp sent via Twilio SID: {msg.sid}")
            except Exception as e:
                alert_record["status"] = f"FAILED: {str(e)}"
                logger.error(f"Failed sending Twilio WhatsApp: {e}")
        else:
            # Sandbox dispatch
            alert_record["status"] = "DELIVERED_SANDBOX"
            logger.info(f"[SANDBOX WHATSAPP DISPATCH] To: {clean_phone}\n{message_body}")

        self._record_history(alert_record)
        return alert_record

    def _record_history(self, record: Dict[str, Any]):
        history = []
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                history = []
        history.insert(0, record)
        history = history[:100]  # Keep last 100 alerts
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error persisting alert history: {e}")

    def get_recent_alerts(self, limit: int = 20) -> list:
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data[:limit]
            except Exception:
                return []
        return []


# Global singleton instance
twilio_client = TwilioWhatsAppClient()
