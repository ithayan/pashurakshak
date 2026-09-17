"""
PashuRakshak Demo Seed Generator
================================
Generates 24 realistic animal profiles using the physiological simulator,
and produces sample video frame fixtures for the computer vision behavioral pipeline.
"""

import os
import sys
import json
import cv2
import numpy as np

# Ensure UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "digital-twin")))
from disease_simulator import DiseaseProgressionSimulator, AnimalProfile

DISTRICTS = ["Pune", "Ahmednagar", "Kolhapur", "Solapur", "Nashik", "Satara"]
BREEDS = ["Gir-HF Cross (गिर संकर)", "Khillari (खिल्लारी)", "Murrah Buffalo (मुर्रा म्हैस)", "Red Kandhari (लाल कंधारी)"]
NAMES = ["लक्ष्मी", "गोदावरी", "राणी", "गंगा", "सोनम", "कस्तुरी", "चमेली", "कावेरी", "मंगला", "अनुसया"]


def generate_seed_data():
    sim = DiseaseProgressionSimulator(seed=999)
    animals = []

    print("Generating 24 realistic cattle profiles via physiological simulator...")
    for i in range(24):
        dist = DISTRICTS[i % len(DISTRICTS)]
        tag_id = f"TAG-{1000 + i}"
        animal_id = f"MAH-{dist[:3].upper()}-{tag_id}"
        name = f"गाय #{i+1} ({NAMES[i % len(NAMES)]})"
        breed = BREEDS[i % len(BREEDS)]
        age = round(3.0 + (i % 6) * 0.8, 1)

        # Distribute conditions: 10 healthy, 5 mastitis, 4 FMD, 3 LSD, 2 BRD
        if i < 10:
            condition = "Healthy"
        elif i < 15:
            condition = "Mastitis"
        elif i < 19:
            condition = "FMD"
        elif i < 22:
            condition = "LSD"
        else:
            condition = "BRD"

        profile = AnimalProfile(
            animal_id=animal_id,
            tag_number=tag_id,
            breed=breed,
            age_years=age,
            lactation_stage_days=40 + i * 8
        )

        timeline = sim.simulate_animal_timeline(profile, condition=condition, days=7, onset_day=3.5)
        recent_day = timeline[-1]
        prev_24h = timeline[-25]

        # Extract 7 daily summary averages
        daily_history = []
        days_label = ["सोम", "मंगळ", "बुध", "गुरू", "शुक्र", "शनि", "आज"]
        for d in range(7):
            d_slice = timeline[d * 24:(d + 1) * 24]
            daily_history.append({
                "day": days_label[d],
                "temperature": round(float(np.mean([x["temperature"] for x in d_slice])), 2),
                "rumination": round(float(np.mean([x["rumination_minutes"] for x in d_slice])), 1),
                "feeding": round(float(np.mean([x["feeding_minutes"] for x in d_slice])), 1),
                "activity": round(float(np.mean([x["activity_index"] for x in d_slice])), 1)
            })

        status = "HEALTHY" if condition == "Healthy" else ("CRITICAL" if condition in ["FMD", "Mastitis"] else "WARNING")

        animals.append({
            "animal_id": animal_id,
            "tag_number": name,
            "district": dist,
            "breed": breed,
            "age": age,
            "status": status,
            "condition": condition,
            "current_vitals": {
                "temperature": recent_day["temperature"],
                "temp_delta_24h": round(recent_day["temperature"] - prev_24h["temperature"], 2),
                "rumination_minutes": recent_day["rumination_minutes"],
                "feeding_minutes": recent_day["feeding_minutes"],
                "activity_index": recent_day["activity_index"]
            },
            "history_7d": daily_history
        })

    out_file = os.path.join(os.path.dirname(__file__), "seed_animals.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(animals, f, indent=2, ensure_ascii=False)
    print(f"Saved 24 seed animals to {out_file}")


def generate_sample_clip_frames():
    clips_dir = os.path.join(os.path.dirname(__file__), "sample_clips")
    os.makedirs(clips_dir, exist_ok=True)

    scenarios = [
        ("01_healthy_grazing.jpg", "Healthy Active Herd Grazing", (0, 200, 0), [(120, 150, 280, 360), (320, 160, 480, 370)]),
        ("02_isolated_recumbent.jpg", "CRITICAL: Cow #42 Isolated & Lying Down", (0, 0, 255), [(40, 260, 260, 430)]),
        ("03_limping_gait.jpg", "WARNING: Cow #18 Abnormal Limping Gait", (0, 165, 255), [(200, 180, 380, 400)]),
        ("04_prolonged_lying.jpg", "WARNING: Prolonged Recumbency in Shed", (0, 215, 255), [(100, 220, 320, 410)])
    ]

    for filename, title, color, boxes in scenarios:
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        # Background barn
        img[:] = (35, 45, 52)
        # Ground
        cv2.rectangle(img, (0, 220), (640, 480), (45, 55, 62), -1)

        cv2.putText(img, "PASHURAKSHAK CCTV FEED [CATTLE SURVEILLANCE]", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(img, title, (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        for b in boxes:
            cv2.rectangle(img, (b[0], b[1]), (b[2], b[3]), color, 3)
            cv2.putText(img, "BOVINE_ANOMALY_TRACKER", (b[0], b[1] - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)

        path = os.path.join(clips_dir, filename)
        cv2.imwrite(path, img)
        print(f"Generated sample fixture: {path}")


if __name__ == "__main__":
    generate_seed_data()
    generate_sample_clip_frames()
