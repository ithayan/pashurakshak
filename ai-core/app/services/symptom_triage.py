"""
PashuRakshak AI Core - Multilingual Rural Symptom Triage Engine (Sub-module C)
=============================================================================
Specialized NLP & Rule-based Diagnostic Triage with deep Marathi (मराठी),
Hindi (हिन्दी), and English veterinary terminology matching rural Maharashtra idioms.

Provides:
- Condition probability matching
- Severity & urgency triage (CRITICAL, MODERATE, ROUTINE)
- Immediate farmer first-aid protocols (in Marathi)
- Spoken audio script text for low-literacy farmers
"""

import re
from typing import List, Dict, Tuple
from app.schemas import SymptomTriageRequest, SymptomTriageResponse, ConditionMatch


# Knowledge Base of Cattle Pathologies with Rural Marathi & Hindi Lexicons
DISEASE_KB = [
    {
        "id": "MASTITIS",
        "name_en": "Bovine Mastitis",
        "name_mr": "कासदाह / मस्टायटीस (स्तनदाह)",
        "name_hi": "थनैला रोग (मस्टाइटिस)",
        "urgency": "CRITICAL",
        "keywords_mr": [
            "कास", "कास सुजली", "कास गरम", "दूध कमी", "दुधात गुठळ्या", "चिबड",
            "रक्ताळलेले दूध", "स्तन", "कासेला सूज", "स्तनात गाठ", "दूध पिवळसर",
            "दोन दिवसांत दूध अर्धे झाले", "कासेला हात लावू देत नाही"
        ],
        "keywords_hi": [
            "थन", "थन में सूजन", "दूध कम", "दूध में खून", "दूध में थक्के", "छिछड़े", "थन गरम"
        ],
        "keywords_en": [
            "mastitis", "udder", "swollen udder", "hot udder", "clots in milk", "blood in milk", "teat", "drop in milk"
        ],
        "actions_mr": [
            "या आजारी गायीचे दूध इतर गायींनंतर शेवटी आणि वेगळ्या भांड्यात काढा.",
            "संसर्ग पसरू नये म्हणून इतर जनावरांना स्पर्श करण्यापूर्वी हात आणि कास स्वच्छ धुवा.",
            "कासेवर कोमट पाण्याची घडी घाला. कासेवर बर्फ किंवा थंड पाण्याचा लेप लावा सूज कमी होईल.",
            "तात्काळ पशुवैद्यकीय दवाखान्यात संपर्क साधा आणि अँटिबायोटिक मलम / CMT चाचणी करा."
        ],
        "audio_script_mr": "शेतकरी बंधू, तुमच्या जनावराला कासदाहाची (मस्टायटीस) तीव्र लक्षणे आहेत. दूध लगेच वेगळे काढा आणि जवळच्या पशुवैद्यकीय अधिकाऱ्यांशी संपर्क साधा. कासेला स्वच्छ कोमट पाण्याने धुवा."
    },
    {
        "id": "FMD",
        "name_en": "Foot-and-Mouth Disease (FMD)",
        "name_mr": "लाळ्या खुरकूत (खुरपका-मुंहपका)",
        "name_hi": "खुरपका-मुंहपका रोग (FMD)",
        "urgency": "CRITICAL",
        "keywords_mr": [
            "लाळ", "लाळ गळणे", "तोंडातून लाळ", "लाळ्या", "खुरकूत", "तोंडाला फोड",
            "जिभेवर व्रण", "खुर सुजले", "लंगडत चालते", "पायाचे खुर", "तोंडात फोड",
            "लाळ गळते", "खुरामध्ये किडे", "गवत चावता येत नाही", "तीव्र ताप"
        ],
        "keywords_hi": [
            "लार टपकना", "मुंह में छाले", "खुर में घाव", "लंगड़ाना", "खुरपका", "मुंहपका", "तेज बुखार"
        ],
        "keywords_en": [
            "fmd", "foot and mouth", "salivation", "drooling saliva", "blisters in mouth", "tongue ulcers", "limping", "hoof lesion", "high fever"
        ],
        "actions_mr": [
            "धोकादायक संसर्गजन्य रोग! या जनावराला गोठ्यातील इतर सर्व जनावरांपासून ताबडतोब ५० फूट दूर वेगळे बांधा.",
            "तोंडातील फोडांवर बोरो-ग्लिसरीन किंवा तुरटीच्या सौम्य पाण्याचा लेप लावा.",
            "खुरांचे व्रण पोटॅशियम परमँगनेट (लाल औषध) किंवा सौम्य फिनाईलच्या पाण्याने स्वच्छ करा.",
            "जनावराला मऊ आणि पातळ दलिया/पेज खायला द्या. इतर गोठ्यातील शेतकऱ्यांना सतर्क करा."
        ],
        "audio_script_mr": "सावधान! हे लाळ्या खुरकूत रोगाचे लक्षण असू शकते. हा रोग वेगाने पसरतो. या जनावराला त्वरित इतर गुरांपासून वेगळे करा आणि गांभीर्याने पशुवैद्यकीय दवाखान्यात कळवा."
    },
    {
        "id": "LSD",
        "name_en": "Lumpy Skin Disease (LSD)",
        "name_mr": "लम्पी त्वचा रोग (LSD)",
        "name_hi": "लम्पी स्किन डिजीज (एलएसडी)",
        "urgency": "CRITICAL",
        "keywords_mr": [
            "लम्पी", "त्वचेवर गाठी", "अंगावर गाठी", "गोळे आले", "गाठी फुटल्या",
            "अंगावर फोड", "पायावर सूज", "डोळ्यातून पाणी", "नाक वाहणे", "त्वचेचे चट्टे",
            "गाठी आल्या आहेत", "सतत ताप"
        ],
        "keywords_hi": [
            "लम्पी", "त्वचा पर गांठें", "शरीर पर फफोले", "गांठ फूटना", "आंख से पानी", "नाक बहना", "गांठें"
        ],
        "keywords_en": [
            "lumpy", "lumpy skin", "skin nodules", "lumps on body", "swollen legs", "ocular discharge", "nasal discharge", "crusts"
        ],
        "actions_mr": [
            "गोठ्यात डास, माश्या, गोचीड यांचा प्रादुर्भाव रोखण्यासाठी कडुनिंबाच्या पानांचा धूर करा व औषध फवारा.",
            "गाठी फुटलेल्या जागेवर हळद आणि खोबरेल तेलाचा लेप लावा.",
            "ताप कमी करण्यासाठी आणि प्रतिकारशक्ती वाढवण्यासाठी गुळ, हळद, मिरी यांचा काढा द्या.",
            "पशुसंवर्धन विभागाच्या लसीकरण पथकाला तात्काळ संपर्क करा."
        ],
        "audio_script_mr": "शेतकरी मित्र, लम्पी रोगाचा संसर्ग माश्या आणि डासांमुळे पसरतो. गोठ्यात डास प्रतिबंधक उपाय करा, जखमेवर हळद लावा आणि सरकारी पशुवैद्यकाला कळवून त्वरित लस/उपचार द्या."
    },
    {
        "id": "BRD",
        "name_en": "Bovine Respiratory Disease (BRD)",
        "name_mr": "बव्हाइन श्वसनदाह / घटसर्प (खोकला व ताप)",
        "name_hi": "श्वसन रोग (निमोनिया/गलघोंटू)",
        "urgency": "MODERATE",
        "keywords_mr": [
            "खोकला", "श्वास", "धाप लागणे", "श्वास वेगाने घेणे", "नाकातून शेम्बूड",
            "घरघर आवाज", "घशावर सूज", "डोळे लाल", "श्वास घेताना त्रास"
        ],
        "keywords_hi": [
            "खांसी", "सांस फूलना", "तेज सांस", "नाक से पानी", "घरघराहट", "गले में सूजन"
        ],
        "keywords_en": [
            "cough", "respiratory", "rapid breathing", "dyspnea", "nasal mucus", "wheezing", "throat swelling"
        ],
        "actions_mr": [
            "जनावराला थंड हवेच्या झोतापासून वाचवा आणि उबदार कोरड्या जागी ठेवा.",
            "निलगिरी तेलाची वाफ दिल्यास श्वास घेण्यास आराम मिळतो.",
            "घटसर्प किंवा न्यूमोनियाचा संशय असल्यास उशीर न करता अँटिबायोटिक उपचारासाठी डॉक्टरांना बोलवा."
        ],
        "audio_script_mr": "जनावराच्या श्वसनलिकेत संसर्ग आहे. जनावराला थंड वाऱ्यापासून वाचवा आणि तात्काळ पशुवैद्यकीय तपासणी करून घ्या."
    },
    {
        "id": "KETOSIS",
        "name_en": "Bovine Ketosis / Indigestion",
        "name_mr": "अपचन / केटॉसिस (रवंथ बंद व पोटफुगी)",
        "name_hi": "अपच / कीटोसिस (जुगाली बंद)",
        "urgency": "MODERATE",
        "keywords_mr": [
            "रवंथ करत नाही", "रवंथ बंद", "चारा खात नाही", "खाणे पिणे सोडले", "पोट फुगले",
            "शेण घट्ट", "शेण पातळ", "सुस्त पडली", "डोळे खोल गेले", "अंग थंड"
        ],
        "keywords_hi": [
            "जुगाली नहीं कर रही", "चारा नहीं खा रही", "पेट फूलना", "गोबर सख्त", "सुस्त"
        ],
        "keywords_en": [
            "not ruminating", "off feed", "bloat", "indigestion", "ketosis", "dull", "stopped eating"
        ],
        "actions_mr": [
            "२०० ग्रॅम गुळ आणि ५० ग्रॅम जिरे-ओवा कोमट पाण्यात मिसळून पाजा.",
            "रवंथ पूर्ववत होण्यासाठी पाचक पावडर (उदा. हिमालयन बतिसा किंवा रुमिफस) द्या.",
            "पोटफुगी असल्यास जनावराला थोडे चालवा आणि ताबडतोब डॉक्टरांचा सल्ला घ्या."
        ],
        "audio_script_mr": "जनावराचे रवंथ थांबले आहे आणि पचनक्रिया मंदावली आहे. जनावराला गुळ-ओव्याचे पाणी द्या आणि हलका चारा टाका."
    }
]


class SymptomTriageService:
    def __init__(self):
        pass

    def detect_language(self, text: str) -> str:
        # Check Devanagari characters
        devanagari_count = len(re.findall(r"[\u0900-\u097F]", text))
        if devanagari_count > 3:
            # Check distinct Marathi grammatical markers:
            # आहे, नाही, झाले, करतो, करत, च, च्या, ची, ला, वर, मुळे, खुरकूत
            marathi_markers = ["आहे", "नाही", "झाले", "झाली", "करत", "कमी", "कास", "लाळ", "खुर", "गाठी", "पोट", "गाय", "म्हैस"]
            if any(m in text for m in marathi_markers):
                return "mr"
            return "hi"
        return "en"

    def triage_symptoms(self, req: SymptomTriageRequest) -> SymptomTriageResponse:
        text = req.query_text.lower().strip()
        lang = req.language or self.detect_language(text)

        matches: List[ConditionMatch] = []

        for disease in DISEASE_KB:
            score = 0.0
            matched_indicators = []

            # Match Marathi keywords
            for kw in disease["keywords_mr"]:
                if kw in text:
                    score += 1.5
                    matched_indicators.append(f"मराठी खूण: '{kw}'")

            # Match Hindi keywords
            for kw in disease["keywords_hi"]:
                if kw in text:
                    score += 1.3
                    matched_indicators.append(f"हिन्दी खूण: '{kw}'")

            # Match English keywords
            for kw in disease["keywords_en"]:
                if kw in text:
                    score += 1.2
                    matched_indicators.append(f"English: '{kw}'")

            if score > 0:
                prob = min(0.96, 0.35 + score * 0.18)
                matches.append(ConditionMatch(
                    condition_name=disease["name_en"],
                    condition_name_mr=disease["name_mr"],
                    probability=round(prob, 2),
                    key_indicators=matched_indicators[:3]
                ))

        # Sort matches by probability
        matches.sort(key=lambda x: x.probability, reverse=True)

        if matches:
            top_match = matches[0]
            # Find disease KB item
            kb_item = next(d for d in DISEASE_KB if d["name_en"] == top_match.condition_name)
            urgency = kb_item["urgency"]
            actions = kb_item["actions_mr"]
            audio_script = kb_item["audio_script_mr"]
            primary_name = top_match.condition_name
            primary_name_mr = top_match.condition_name_mr
        else:
            # Generic baseline response
            primary_name = "Undetermined Malaise"
            primary_name_mr = "अस्पष्ट शारीरिक अस्वस्थता (सर्वसाधारण तपासणी आवश्यक)"
            urgency = "ROUTINE"
            actions = [
                "जनावराचे तापमान थर्मामीटरने तपासा (सामान्य तापमान: ३८.५° से. / १०१.५° फॅ.).",
                "स्वच्छ व ताजे पाणी मुबलक प्रमाणात पिण्यास द्या.",
                "लक्षणे २४ तासांत न सुधारल्यास नजीकच्या तालुका पशुवैद्यकीय दवाखान्यात संपर्क साधा."
            ]
            audio_script = "तुमच्या वर्णनावरून निश्चित आजार ओळखता आला नाही. कृपया जनावराचे तापमान मोजा आणि पशुवैद्यकीय अधिकाऱ्यांशी सल्लामसलत करा."
            matches = [ConditionMatch(
                condition_name="General Malaise",
                condition_name_mr="सर्वसाधारण अशक्तपणा",
                probability=0.45,
                key_indicators=["अस्पष्ट लक्षणे"]
            )]

        return SymptomTriageResponse(
            input_query=req.query_text,
            detected_language=lang,
            primary_condition=primary_name,
            primary_condition_mr=primary_name_mr,
            urgency_level=urgency,
            probable_conditions=matches,
            immediate_farmer_actions=actions,
            marathi_audio_prompt_text=audio_script,
            nearest_dispensary_advice="महाराष्ट्र शासन पशुसंवर्धन विभाग - मोफत हेल्पलाईन १९६२ वर संपर्क करा किंवा नजीकच्या तालुका पशुवैद्यकीय दवाखान्याशी संपर्क साधा."
        )


# Global singleton instance
triage_service = SymptomTriageService()
