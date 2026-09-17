/**
 * PashuRakshak Farmer App - API Client & Mock Seed Data
 */

const API_BASE = "http://localhost:8000";

const SEED_HERD = [
  {
    animal_id: "MAH-PUN-042",
    tag_number: "गाय #४२ (लक्ष्मी)",
    breed: "गिर संकर (Gir-HF Cross)",
    age: 4.5,
    lactation_day: 82,
    status: "CRITICAL",
    risk_prob: 0.88,
    condition_code: "Mastitis",
    condition_name_mr: "कासदाह / मस्टायटीस (स्तनदाह)",
    condition_name_en: "Bovine Mastitis",
    lead_time_days: 2.5,
    last_updated: "१० मिनिटांपूर्वी",
    vitals: {
      temperature: 39.6,
      rumination_minutes: 290,
      rum_drop_pct: 35.5,
      feeding_minutes: 175,
      feed_drop_pct: 31.0,
      activity_index: 72,
      act_drop_pct: 27.5
    },
    action_mr: "दूध तात्काळ वेगळे काढा. कास कोमट पाण्याने स्वच्छ धुवा आणि पशुवैद्यकीय अधिकाऱ्यांशी संपर्क साधा. (CMT चाचणी आवश्यक)",
    action_en: "Isolate milk immediately. Clean quarters with warm water and disinfectant. Call veterinary officer for CMT test.",
    history: [
      { day: "सोम", temp: 38.5, rumination: 470, feeding: 260, activity: 102 },
      { day: "मंगळ", temp: 38.6, rumination: 465, feeding: 255, activity: 98 },
      { day: "बुध", temp: 38.6, rumination: 450, feeding: 250, activity: 95 },
      { day: "गुरू", temp: 38.8, rumination: 410, feeding: 235, activity: 90 },
      { day: "शुक्र", temp: 39.1, rumination: 360, feeding: 210, activity: 82 },
      { day: "शनि", temp: 39.4, rumination: 315, feeding: 190, activity: 76 },
      { day: "आज", temp: 39.6, rumination: 290, feeding: 175, activity: 72 }
    ],
    vaccinations: [
      { name: "FMD (लाळ्या खुरकूत) लस", date: "१५ मे २०२६", status: "DONE" },
      { name: "लम्पी स्किन रोग प्रतिबंधक लस", date: "१० फेब्रुवारी २०२६", status: "DONE" },
      { name: "जंतनाशक औषध", date: "०१ ऑगस्ट २०२६", status: "DONE" },
      { name: "बुस्टर डोस (घटसर्प)", date: "२५ सप्टेंबर २०२६", status: "DUE" }
    ]
  },
  {
    animal_id: "MAH-AHM-018",
    tag_number: "गाय #१८ (गोदावरी)",
    breed: "खिल्लारी (Khillari)",
    age: 3.8,
    lactation_day: 45,
    status: "WARNING",
    risk_prob: 0.74,
    condition_code: "FMD",
    condition_name_mr: "लाळ्या खुरकूत संशय (खुर समस्या)",
    condition_name_en: "Suspected FMD / Lameness",
    lead_time_days: 1.8,
    last_updated: "२५ मिनिटांपूर्वी",
    vitals: {
      temperature: 40.2,
      rumination_minutes: 340,
      rum_drop_pct: 26.0,
      feeding_minutes: 190,
      feed_drop_pct: 26.9,
      activity_index: 64,
      act_drop_pct: 36.0
    },
    action_mr: "जनावराला कळपापासून ५० फूट दूर वेगळे बांधा. खूर आणि तोंडाची तपासणी करा. लाल औषधाच्या पाण्याने खूर धुवा.",
    action_en: "Quarantine cow 50ft from herd. Inspect hooves and oral cavity for vesicles. Wash hooves with potassium permanganate.",
    history: [
      { day: "सोम", temp: 38.4, rumination: 460, feeding: 265, activity: 104 },
      { day: "मंगळ", temp: 38.5, rumination: 455, feeding: 260, activity: 101 },
      { day: "बुध", temp: 38.6, rumination: 440, feeding: 250, activity: 97 },
      { day: "गुरू", temp: 38.9, rumination: 420, feeding: 240, activity: 91 },
      { day: "शुक्र", temp: 39.4, rumination: 390, feeding: 220, activity: 80 },
      { day: "शनि", temp: 39.8, rumination: 360, feeding: 200, activity: 70 },
      { day: "आज", temp: 40.2, rumination: 340, feeding: 190, activity: 64 }
    ],
    vaccinations: [
      { name: "लाळ्या खुरकूत लस (FMD)", date: "२० जानेवारी २०२६", status: "DONE" },
      { name: "लम्पी लस", date: "०५ मार्च २०२६", status: "DONE" }
    ]
  },
  {
    animal_id: "MAH-KOL-009",
    tag_number: "म्हैस #०९ (मुर्रा राणी)",
    breed: "मुर्रा म्हैस (Murrah Buffalo)",
    age: 5.2,
    lactation_day: 110,
    status: "HEALTHY",
    risk_prob: 0.08,
    condition_code: "Healthy",
    condition_name_mr: "निरोगी (सामान्य)",
    condition_name_en: "Healthy",
    lead_time_days: 0,
    last_updated: "२ तासांपूर्वी",
    vitals: {
      temperature: 38.4,
      rumination_minutes: 480,
      rum_drop_pct: 0.0,
      feeding_minutes: 270,
      feed_drop_pct: 0.0,
      activity_index: 99,
      act_drop_pct: 0.0
    },
    action_mr: "पशूचे आरोग्य उत्तम आहे. संतुलित खुराक आणि ताजे स्वच्छ पाणी चालू ठेवा.",
    action_en: "Animal is in prime health. Maintain balanced feed and fresh water.",
    history: [
      { day: "सोम", temp: 38.3, rumination: 475, feeding: 270, activity: 98 },
      { day: "मंगळ", temp: 38.4, rumination: 480, feeding: 265, activity: 100 },
      { day: "बुध", temp: 38.4, rumination: 478, feeding: 272, activity: 99 },
      { day: "गुरू", temp: 38.5, rumination: 482, feeding: 270, activity: 97 },
      { day: "शुक्र", temp: 38.4, rumination: 479, feeding: 268, activity: 99 },
      { day: "शनि", temp: 38.4, rumination: 481, feeding: 271, activity: 101 },
      { day: "आज", temp: 38.4, rumination: 480, feeding: 270, activity: 99 }
    ],
    vaccinations: [
      { name: "FMD लस", date: "०२ एप्रिल २०२६", status: "DONE" },
      { name: "एच.एस. (घटसर्प)", date: "१२ जून २०२६", status: "DONE" }
    ]
  },
  {
    animal_id: "MAH-SOL-027",
    tag_number: "गाय #२७ (सोनम)",
    breed: "लाल कंधारी (Red Kandhari)",
    age: 4.0,
    lactation_day: 130,
    status: "HEALTHY",
    risk_prob: 0.12,
    condition_code: "Healthy",
    condition_name_mr: "निरोगी (सामान्य)",
    condition_name_en: "Healthy",
    lead_time_days: 0,
    last_updated: "३ तासांपूर्वी",
    vitals: {
      temperature: 38.5,
      rumination_minutes: 465,
      rum_drop_pct: 0.0,
      feeding_minutes: 255,
      feed_drop_pct: 0.0,
      activity_index: 102,
      act_drop_pct: 0.0
    },
    action_mr: "आरोग्य उत्तम आहे. नियमित देखभाल चालू ठेवा.",
    action_en: "Normal vitals. Routine monitoring.",
    history: [
      { day: "सोम", temp: 38.4, rumination: 460, feeding: 250, activity: 100 },
      { day: "मंगळ", temp: 38.5, rumination: 462, feeding: 252, activity: 101 },
      { day: "बुध", temp: 38.5, rumination: 464, feeding: 254, activity: 102 },
      { day: "गुरू", temp: 38.6, rumination: 461, feeding: 253, activity: 100 },
      { day: "शुक्र", temp: 38.5, rumination: 465, feeding: 255, activity: 103 },
      { day: "शनि", temp: 38.5, rumination: 463, feeding: 256, activity: 101 },
      { day: "आज", temp: 38.5, rumination: 465, feeding: 255, activity: 102 }
    ],
    vaccinations: [
      { name: "FMD लस", date: "१४ मार्च २०२६", status: "DONE" }
    ]
  }
];

class AppAPI {
  static async checkBackendHealth() {
    try {
      const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(2000) });
      return await res.json();
    } catch (e) {
      return { status: "OFFLINE_FALLBACK", onnx_runtime_active: true };
    }
  }

  static async predictHealthRisk(vitalsPayload) {
    try {
      const res = await fetch(`${API_BASE}/predict/health-risk`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(vitalsPayload),
        signal: AbortSignal.timeout(3500)
      });
      return await res.json();
    } catch (e) {
      console.warn("Backend offline, utilizing client-side surrogate fallback.");
      return null;
    }
  }

  static async triageSymptom(queryText, language = "mr") {
    try {
      // Query Veterinary RAG (Retrieval-Augmented Generation) engine
      const res = await fetch(`${API_BASE}/rag/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: queryText, top_k: 2 }),
        signal: AbortSignal.timeout(3500)
      });
      const data = await res.json();
      if (data.status === "SUCCESS" && data.retrieved_protocols && data.retrieved_protocols.length > 0) {
        const top = data.retrieved_protocols[0];
        const actions = top.treatment_and_firstaid_mr.split("\n").filter(a => a.trim().length > 0);
        return {
          primary_condition: data.primary_condition,
          primary_condition_mr: data.primary_condition_mr,
          urgency_level: "CRITICAL",
          confidence_pct: data.confidence_pct,
          verified_citations: data.verified_citations,
          clinical_evidence: top.clinical_evidence,
          ayurvedic_evm_mr: top.ayurvedic_evm_mr,
          isolation_protocol_mr: top.isolation_protocol_mr,
          immediate_farmer_actions: actions,
          marathi_audio_prompt_text: `सावधान! आपल्या जनावरात ${data.primary_condition_mr} आजाराची लक्षणे आढळली आहेत. कृपया त्वरित अलगीकरण करा आणि १९६२ हेल्पलाईनवर संपर्क साधा.`,
          nearest_dispensary_advice: data.helpline
        };
      }
    } catch (e) {
      console.warn("RAG query failed or offline, utilizing client-side triage fallback.");
    }
    return AppAPI.localTriageFallback(queryText);
  }

  static localTriageFallback(text) {
    const lower = text.toLowerCase();
    if (lower.includes("कास") || lower.includes("दूध") || lower.includes("मस्टायटीस") || lower.includes("थन")) {
      return {
        primary_condition: "Bovine Mastitis",
        primary_condition_mr: "कासदाह / मस्टायटीस (स्तनदाह)",
        urgency_level: "CRITICAL",
        immediate_farmer_actions: [
          "या आजारी गायीचे दूध इतर गायींनंतर शेवटी आणि वेगळ्या भांड्यात काढा.",
          "कास कोमट पाण्याने स्वच्छ धुवा आणि थनांना जंतुनाशक लावा.",
          "तात्काळ पशुवैद्यकीय दवाखान्यात संपर्क साधा आणि CMT चाचणी करा."
        ],
        marathi_audio_prompt_text: "शेतकरी बंधू, तुमच्या जनावराला कासदाहाची लक्षणे आहेत. दूध वेगळे काढा आणि डॉक्टरांना दाखवा.",
        nearest_dispensary_advice: "महाराष्ट्र शासन पशुसंवर्धन हेल्पलाईन: १९६२"
      };
    } else if (lower.includes("लाळ") || lower.includes("खुर") || lower.includes("लंगडत")) {
      return {
        primary_condition: "Foot-and-Mouth Disease (FMD)",
        primary_condition_mr: "लाळ्या खुरकूत (खुरपका-मुंहपका)",
        urgency_level: "CRITICAL",
        immediate_farmer_actions: [
          "या जनावराला गोठ्यातील इतर जनावरांपासून ताबडतोब ५० फूट दूर वेगळे बांधा.",
          "तोंडातील फोड आणि खूर पोटॅशियम परमँगनेटच्या सौम्य पाण्याने धुवा.",
          "तात्काळ पशुवैद्यकीय अधिकाऱ्याला संपर्क करा."
        ],
        marathi_audio_prompt_text: "सावधान! लाळ्या खुरकूत रोग वेगाने पसरतो. जनावराला तात्काळ वेगळे करा.",
        nearest_dispensary_advice: "महाराष्ट्र शासन पशुसंवर्धन हेल्पलाईन: १९६२"
      };
    } else {
      return {
        primary_condition: "Bovine Indigestion / Ketosis",
        primary_condition_mr: "अपचन / केटॉसिस (मंद पचन)",
        urgency_level: "MODERATE",
        immediate_farmer_actions: [
          "जनावराला गुळ-ओव्याचे कोमट पाणी द्या.",
          "रवंथ पूर्ववत होण्यासाठी पाचक पावडर द्या.",
          "लक्षणे २४ तासांत न सुधारल्यास पशुवैद्यकाला दाखवा."
        ],
        marathi_audio_prompt_text: "जनावराचे पचन मंदावले आहे. गुळ-ओव्याचे पाणी द्या.",
        nearest_dispensary_advice: "महाराष्ट्र शासन पशुसंवर्धन हेल्पलाईन: १९६२"
      };
    }
  }
}
