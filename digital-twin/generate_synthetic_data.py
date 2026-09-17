"""
PashuRakshak Digital Twin - Synthetic Cohort Dataset Generator
============================================================
Generates 2,400+ simulated cattle cohorts across Maharashtra districts
(Pune, Ahmednagar, Kolhapur, Solapur, Nashik, Sangli, Satara)
to form a physiologically-grounded training & benchmark dataset.
"""

import os
import random
import pandas as pd
import numpy as np
from disease_simulator import DiseaseProgressionSimulator, AnimalProfile

DISTRICTS = ["PUN", "AHM", "KOL", "SOL", "NAS", "SAN", "SAT"]
BREEDS = ["Gir Cross", "Khillari", "Red Kandhari", "Dangi", "Murrah Buffalo", "HF Cross"]
CONDITIONS = ["Healthy", "Mastitis", "FMD", "LSD", "BRD", "Ketosis"]


def generate_cohort_dataset(num_animals: int = 2400, output_csv: str = "data/synthetic_cattle_cohorts.csv"):
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    sim = DiseaseProgressionSimulator(seed=2026)

    records = []
    print(f"Generating synthetic cohort dataset for {num_animals} animals...")

    for i in range(num_animals):
        dist = random.choice(DISTRICTS)
        tag_num = f"TAG-{1000 + i}"
        animal_id = f"MAH-{dist}-{tag_num}"
        breed = random.choice(BREEDS)
        age = round(random.uniform(2.0, 9.0), 1)
        lact_days = random.randint(15, 240)

        # Baseline vitals per breed
        base_temp = 38.4 if "Buffalo" in breed else 38.5
        base_rum = 470.0 if "Cross" in breed else 450.0
        base_feed = 260.0
        base_act = 100.0

        profile = AnimalProfile(
            animal_id=animal_id,
            tag_number=tag_num,
            breed=breed,
            age_years=age,
            lactation_stage_days=lact_days,
            base_temperature=base_temp,
            base_rumination=base_rum,
            base_feeding=base_feed,
            base_activity=base_act
        )

        # Condition distribution: 40% healthy, 60% diseases evenly distributed
        if random.random() < 0.35:
            condition = "Healthy"
        else:
            condition = random.choice(["Mastitis", "FMD", "LSD", "BRD", "Ketosis"])

        onset_day = round(random.uniform(4.0, 9.0), 1)
        subclinical_dur = round(random.uniform(1.8, 3.2), 1)

        timeline = sim.simulate_animal_timeline(
            profile,
            condition=condition,
            days=14,
            onset_day=onset_day,
            subclinical_duration_days=subclinical_dur
        )

        # Sample observation windows: early subclinical, mid subclinical, clinical, or healthy baseline
        # Let's take multiple sample snapshots per animal to capture progression
        sample_hours = [
            int((onset_day - 2.0) * 24),  # Healthy pre-onset
            int((onset_day + subclinical_dur * 0.4) * 24),  # Early subclinical
            int((onset_day + subclinical_dur * 0.85) * 24), # Late subclinical (crucial early warning window!)
            int((onset_day + subclinical_dur + 1.5) * 24)   # Overt clinical
        ]

        for sh in sample_hours:
            if sh < 24 or sh >= len(timeline):
                continue
            curr = timeline[sh]
            prev_24 = timeline[sh - 24]

            # Compute features that collar/ear-tag APIs report
            temp_curr = curr["temperature"]
            temp_24h_delta = round(temp_curr - prev_24["temperature"], 2)

            # 24h rolling average
            window_24 = timeline[sh - 24:sh + 1]
            temp_24h_mean = round(float(np.mean([w["temperature"] for w in window_24])), 2)

            rum_curr = curr["rumination_minutes"]
            rum_drop_pct = round(((base_rum - rum_curr) / base_rum) * 100.0, 1)

            feed_curr = curr["feeding_minutes"]
            feed_drop_pct = round(((base_feed - feed_curr) / base_feed) * 100.0, 1)

            act_curr = curr["activity_index"]
            act_drop_pct = round(((base_act - act_curr) / base_act) * 100.0, 1)

            state = curr["health_state"]
            cond = "Healthy" if state == "Healthy" else curr["condition"]

            # Estimate days to overt clinical signs
            if state == "Healthy":
                days_to_symptom = -1.0
            elif state == "Sub-clinical":
                days_to_symptom = round(max(0.2, (onset_day + subclinical_dur) - curr["day"]), 1)
            else:
                days_to_symptom = 0.0

            records.append({
                "animal_id": animal_id,
                "district": dist,
                "breed": breed,
                "age_years": age,
                "hour": sh,
                "temperature": temp_curr,
                "temp_24h_delta": temp_24h_delta,
                "temp_24h_mean": temp_24h_mean,
                "rumination_minutes": rum_curr,
                "rumination_drop_pct": rum_drop_pct,
                "feeding_minutes": feed_curr,
                "feeding_drop_pct": feed_drop_pct,
                "activity_index": act_curr,
                "activity_drop_pct": act_drop_pct,
                "health_state": state,
                "condition": cond,
                "days_to_symptom": days_to_symptom
            })

    df = pd.DataFrame(records)
    df.to_csv(output_csv, index=False)
    print(f"Successfully generated {len(df)} feature snapshots into {output_csv}")
    print(df["condition"].value_counts())
    return df


if __name__ == "__main__":
    generate_cohort_dataset(
        num_animals=1200,
        output_csv="C:/Users/91900/.gemini/antigravity-ide/scratch/pashurakshak/digital-twin/data/synthetic_cattle_cohorts.csv"
    )
