"""
PashuRakshak AI Core - ONNX Inference Service (Sub-module B)
============================================================
Executes ultra-low latency (<3ms) inference on the pre-trained ONNX
livestock health surrogate model, returning calibrated disease probabilities,
days-to-symptom early warning estimate, and multilingual recommendations.
"""

import os
import json
import logging
from typing import List, Dict, Optional, Tuple
import numpy as np
import onnxruntime as ort
from app.config import ONNX_MODEL_PATH, MODEL_METADATA_PATH, HIGH_RISK_THRESHOLD, MEDIUM_RISK_THRESHOLD
from app.schemas import VitalSignsInput, HealthRiskResponse

logger = logging.getLogger("pashurakshak.onnx")

# Multilingual localized names and recommendations
TRANSLATIONS = {
    "Healthy": {
        "mr": "निरोगी (सामान्य)",
        "hi": "स्वस्थ (सामान्य)",
        "en": "Healthy (Normal)",
        "action_mr": "पशूचे आरोग्य उत्तम आहे. नेहमीप्रमाणे आहार आणि पाणी चालू ठेवा.",
        "action_hi": "पशु स्वस्थ है। सामान्य आहार और पानी जारी रखें।",
        "action_en": "Animal is in optimal health. Maintain standard nutrition and clean water."
    },
    "Mastitis": {
        "mr": "कासदाह / मस्टायटीस (स्तनदाह)",
        "hi": "थनैला रोग (मस्टाइटिस)",
        "en": "Bovine Mastitis (Sub-clinical)",
        "action_mr": "तातडीने या जनावराचे दूध वेगळे काढा. कास कोमट पाण्याने स्वच्छ करा आणि पशुवैद्यकाला दाखवून कॅलिफोर्निया मस्टायटीस टेस्ट (CMT) करून घ्या. संसर्ग पसरू नये म्हणून वेगळे बांधा.",
        "action_hi": "तुरंत इस पशु का दूध अलग निकालें। थन को गुनगुने पानी से साफ करें और पशु चिकित्सक से CMT जांच करवाएं।",
        "action_en": "Isolate animal milk immediately. Strip quarters cleanly and perform California Mastitis Test (CMT). Disinfect teats with post-dip."
    },
    "FMD": {
        "mr": "लाळ्या खुरकूत (खुरपका-मुंहपका)",
        "hi": "खुरपका-मुंहपका रोग (FMD)",
        "en": "Foot-and-Mouth Disease (FMD)",
        "action_mr": "अतिशय संसर्गजन्य! या जनावराला तत्काळ इतर जनावरांपासून पूर्णपणे वेगळे करा. तोंड आणि खुरांना पोटॅशियम परमँगनेटच्या सौम्य पाण्याने धुवा. गावात पशुवैद्यकीय अधिकाऱ्याला तात्काळ कळवा.",
        "action_hi": "अत्यंत संक्रामक! तुरंत अलग बाड़े में रखें। मुंह और खुरों को पोटाश के हल्के घोल से धोएं। नजदीकी पशु अस्पताल को सूचित करें।",
        "action_en": "HIGHLY CONTAGIOUS! Impose strict quarantine immediately. Wash mouth and hooves with 0.1% potassium permanganate solution. Report outbreak to district veterinary officer."
    },
    "LSD": {
        "mr": "लम्पी त्वचा रोग (LSD)",
        "hi": "लम्पी स्किन डिजीज (एलएसडी)",
        "en": "Lumpy Skin Disease (LSD)",
        "action_mr": "त्वचेवरील गाठी तपासा. गोठ्यात डास, माश्या आणि गोचीड प्रतिबंधक फवारणी करा. ताप कमी करण्यासाठी पशुवैद्यकाच्या सल्ल्याने पॅरासिटामॉल द्या.",
        "action_hi": "त्वचा की गांठों की जांच करें। बाड़े में मक्खी-मच्छर रोधी दवा का छिड़काव करें। बुखार के लिए डॉक्टर की सलाह लें।",
        "action_en": "Inspect skin for circular nodules. Vector control (mosquito/tick eradication) is vital. Provide supportive antipyretics under veterinary supervision."
    },
    "BRD": {
        "mr": "बव्हाइन श्वसनदाह (खोकला/फुफ्फुसदाह)",
        "hi": "श्वसन रोग (निमोनिया)",
        "en": "Bovine Respiratory Disease (BRD)",
        "action_mr": "जनावराला कोरड्या आणि हवेशीर जागी ठेवा. श्वास घेण्याचा वेग तपासा. थंड वाऱ्यापासून संरक्षण करा आणि तात्काळ अँटिबायोटिक उपचारासाठी डॉक्टरांना बोलवा.",
        "action_hi": "पशु को सूखी व हवादार जगह रखें। ठंड से बचाएं और डॉक्टर को दिखाकर श्वसन उपचार शुरू करें।",
        "action_en": "Relocate animal to a dry, well-ventilated stall away from drafts. Administer NSAID and veterinary-prescribed antibiotic."
    },
    "Ketosis": {
        "mr": "केटॉसिस (ऊर्जा कमतरता / मंद पचन)",
        "hi": "कीटोसिस (उपापचय विकार)",
        "en": "Bovine Ketosis (Negative Energy Balance)",
        "action_mr": "जनावराच्या शरीरात साखरेची कमतरता आहे. गुळ-पाणी किंवा प्रोपीलीन ग्लायकॉल तोंडाने द्या. रवंथ वाढवण्यासाठी उत्तम प्रतीचा हिरवा चारा द्या.",
        "action_hi": "पशु में ग्लूकोज की कमी है। गुड़-पानी या प्रोपलीन ग्लाइकोल दें। अच्छी गुणवत्ता का हरा चारा खिलाएं।",
        "action_en": "Subacute energy deficit. Administer oral propylene glycol drench or IV dextrose. Enhance glucogenic feed precursors."
    }
}


class ONNXPredictionService:
    def __init__(self):
        self.session = None
        self.metadata = None
        self._load_model()

    def _load_model(self):
        try:
            if os.path.exists(ONNX_MODEL_PATH) and os.path.exists(MODEL_METADATA_PATH):
                logger.info(f"Loading ONNX model from {ONNX_MODEL_PATH}")
                self.session = ort.InferenceSession(ONNX_MODEL_PATH)
                with open(MODEL_METADATA_PATH, "r") as f:
                    self.metadata = json.load(f)
                logger.info("ONNX model and metadata loaded successfully.")
            else:
                logger.warning(f"ONNX model or metadata not found at {ONNX_MODEL_PATH}. Prediction service running in fallback mode.")
        except Exception as e:
            logger.error(f"Error loading ONNX model: {e}")

    def predict(self, vitals: VitalSignsInput) -> HealthRiskResponse:
        # Default fallback baselines if optional derivatives are omitted
        t_delta = vitals.temp_24h_delta if vitals.temp_24h_delta is not None else 0.0
        t_mean = vitals.temp_24h_mean if vitals.temp_24h_mean is not None else vitals.temperature
        r_drop = vitals.rumination_drop_pct if vitals.rumination_drop_pct is not None else max(0.0, ((460.0 - vitals.rumination_minutes) / 460.0) * 100.0)
        f_drop = vitals.feeding_drop_pct if vitals.feeding_drop_pct is not None else max(0.0, ((260.0 - vitals.feeding_minutes) / 260.0) * 100.0)
        a_drop = vitals.activity_drop_pct if vitals.activity_drop_pct is not None else max(0.0, ((100.0 - vitals.activity_index) / 100.0) * 100.0)

        raw_features = [
            vitals.temperature,
            t_delta,
            t_mean,
            vitals.rumination_minutes,
            r_drop,
            vitals.feeding_minutes,
            f_drop,
            vitals.activity_index,
            a_drop
        ]

        classes = ["Healthy", "Mastitis", "FMD", "LSD", "BRD", "Ketosis"]
        days_estimate = 0.0

        if self.session and self.metadata:
            # Standardize using trained statistics
            means = np.array(self.metadata["means"], dtype=np.float32)
            stds = np.array(self.metadata["stds"], dtype=np.float32)
            norm_features = (np.array(raw_features, dtype=np.float32) - means) / stds
            input_tensor = norm_features.reshape(1, -1)

            input_name = self.session.get_inputs()[0].name
            ort_outs = self.session.run(None, {input_name: input_tensor})
            probs = ort_outs[0][0].tolist()
            days_estimate = round(float(ort_outs[1][0][0]), 1)
        else:
            # Analytical fallback in case model is absent
            probs = self._analytical_fallback_probs(vitals)
            days_estimate = 1.5 if max(probs[1:]) > 0.4 else 0.0

        # Create detailed probabilities dictionary
        prob_dict = {classes[i]: round(probs[i], 3) for i in range(len(classes))}

        # Find top predicted condition
        top_idx = int(np.argmax(probs))
        top_condition = classes[top_idx]
        top_prob = round(probs[top_idx], 3)

        # Evaluate risk level
        if top_condition == "Healthy":
            risk_level = "LOW"
            is_early_warning = False
            dispatch_alert = False
        else:
            if top_prob >= HIGH_RISK_THRESHOLD:
                risk_level = "HIGH"
                dispatch_alert = True
            elif top_prob >= MEDIUM_RISK_THRESHOLD:
                risk_level = "MEDIUM"
                dispatch_alert = False
            else:
                risk_level = "LOW"
                dispatch_alert = False
            is_early_warning = days_estimate > 0.3

        # Formulate localized names and instructions
        lang = vitals.language or "mr"
        trans = TRANSLATIONS.get(top_condition, TRANSLATIONS["Healthy"])
        localized_condition = f"{trans.get(lang, trans['mr'])} ({top_condition})"
        localized_action = trans.get(f"action_{lang}", trans["action_mr"])

        return HealthRiskResponse(
            animal_id=vitals.animal_id,
            risk_level=risk_level,
            disease_probability=top_prob,
            likely_condition=localized_condition,
            condition_code=top_condition,
            days_to_symptom_estimate=days_estimate,
            is_early_warning=is_early_warning,
            recommended_action=localized_action,
            detailed_probabilities=prob_dict,
            dispatch_whatsapp_alert=dispatch_alert
        )

    def _analytical_fallback_probs(self, vitals: VitalSignsInput) -> List[float]:
        """Heuristic calculation if ONNX runtime is uninitialized."""
        p_healthy = 0.8
        p_mast = 0.05
        p_fmd = 0.03
        p_lsd = 0.04
        p_brd = 0.04
        p_ket = 0.04

        if vitals.temperature > 39.2 and vitals.rumination_minutes < 380:
            p_mast += 0.5
            p_healthy -= 0.5
        if vitals.temperature > 40.2 and vitals.activity_index < 70:
            p_fmd += 0.6
            p_healthy -= 0.5
        if vitals.temperature <= 38.6 and vitals.rumination_minutes < 260:
            p_ket += 0.5
            p_healthy -= 0.4

        raw = [p_healthy, p_mast, p_fmd, p_lsd, p_brd, p_ket]
        s = sum(raw)
        return [max(0.01, r / s) for r in raw]


# Global singleton instance
onnx_service = ONNXPredictionService()
