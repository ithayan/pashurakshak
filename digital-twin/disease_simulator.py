"""
PashuRakshak Digital Twin - Compartmental Disease Progression Simulator
======================================================================
Simulates physiological dynamics of cattle (Bos indicus / Bos taurus crossbreeds)
based on veterinary literature and compartmental disease progression models.

Modeled Biomarkers:
- Body Temperature (°C): Baseline 38.5 ± 0.3°C, diurnal circadian fluctuation
- Rumination Time (min/day): Baseline 450 ± 40 min/day
- Feeding Duration (min/day): Baseline 260 ± 30 min/day
- Activity Index (rel. unit): Baseline 100 ± 12 units

Conditions modeled:
- 0: Healthy
- 1: Mastitis (कासदाह) - early rumination drop 48-72h prior to clinical signs
- 2: Foot-and-Mouth Disease (FMD / लाळ्या खुरकूत) - severe pyrexia, acute feeding/activity collapse
- 3: Lumpy Skin Disease (LSD / लम्पी त्वचा रोग) - biphasic fever, systemic depression
- 4: Bovine Respiratory Disease (BRD / श्वसनदाह) - sustained fever, progressive activity decline
- 5: Ketosis (केटॉसिस) - severe rumination drop without fever (often sub-normal temp)
"""

import math
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np


@dataclass
class AnimalProfile:
    animal_id: str
    tag_number: str
    breed: str
    age_years: float
    lactation_stage_days: int
    base_temperature: float = 38.5
    base_rumination: float = 460.0  # min/day
    base_feeding: float = 260.0     # min/day
    base_activity: float = 100.0    # relative index


class DiseaseProgressionSimulator:
    """Simulates physiological time-series over a defined day horizon."""

    CONDITIONS = ["Healthy", "Mastitis", "FMD", "LSD", "BRD", "Ketosis"]

    def __init__(self, seed: int = 42):
        random.seed(seed)
        np.random.seed(seed)

    def simulate_animal_timeline(
        self,
        profile: AnimalProfile,
        condition: str,
        days: int = 14,
        onset_day: float = 8.0,
        subclinical_duration_days: float = 2.5
    ) -> List[Dict]:
        """
        Generates hourly physiological readings over `days` (total 24 * days steps).
        Onset of disease begins at `onset_day`.
        Sub-clinical phase lasts `subclinical_duration_days` before overt clinical signs.
        """
        hours = days * 24
        onset_hour = onset_day * 24
        subclinical_hours = subclinical_duration_days * 24
        clinical_hour = onset_hour + subclinical_hours

        readings = []

        # Animal individual baseline offset
        indiv_temp = profile.base_temperature + random.gauss(0, 0.15)
        indiv_rum = profile.base_rumination + random.gauss(0, 20.0)
        indiv_feed = profile.base_feeding + random.gauss(0, 15.0)
        indiv_act = profile.base_activity + random.gauss(0, 6.0)

        for h in range(hours):
            t_day = h / 24.0
            circadian_phase = 2 * math.pi * ((h % 24) - 6) / 24.0  # lowest at 6 AM, highest at 6 PM
            circadian_temp = 0.35 * math.sin(circadian_phase)
            circadian_rum = 30.0 * math.cos(circadian_phase)
            circadian_feed = 20.0 * math.sin(circadian_phase)
            circadian_act = 15.0 * math.sin(circadian_phase)

            # Sensor random jitter
            noise_temp = random.gauss(0, 0.08)
            noise_rum = random.gauss(0, 8.0)
            noise_feed = random.gauss(0, 6.0)
            noise_act = random.gauss(0, 4.0)

            # Determine disease state
            if condition == "Healthy" or h < onset_hour:
                state = "Healthy"
                disease_progress = 0.0  # [0.0, 1.0]
            elif h < clinical_hour:
                state = "Sub-clinical"
                disease_progress = (h - onset_hour) / subclinical_hours * 0.5  # 0 to 0.5
            else:
                state = "Clinical"
                post_clinical_hrs = h - clinical_hour
                disease_progress = 0.5 + 0.5 * (1.0 - math.exp(-post_clinical_hrs / 48.0))

            # Physiological effect multipliers according to condition
            delta_temp, delta_rum, delta_feed, delta_act = self._compute_biomarker_deltas(
                condition, state, disease_progress
            )

            # Final values
            curr_temp = round(indiv_temp + circadian_temp + delta_temp + noise_temp, 2)
            curr_rum = max(40.0, round(indiv_rum + circadian_rum + delta_rum + noise_rum, 1))
            curr_feed = max(20.0, round(indiv_feed + circadian_feed + delta_feed + noise_feed, 1))
            curr_act = max(15.0, round(indiv_act + circadian_act + delta_act + noise_act, 1))

            readings.append({
                "animal_id": profile.animal_id,
                "hour": h,
                "day": round(t_day, 2),
                "condition": condition,
                "health_state": state,
                "disease_progress": round(disease_progress, 3),
                "temperature": curr_temp,
                "rumination_minutes": curr_rum,
                "feeding_minutes": curr_feed,
                "activity_index": curr_act
            })

        return readings

    def _compute_biomarker_deltas(
        self, condition: str, state: str, progress: float
    ) -> Tuple[float, float, float, float]:
        """Calculates delta offsets based on veterinary pathophysiology."""
        if state == "Healthy" or progress <= 0:
            return 0.0, 0.0, 0.0, 0.0

        if condition == "Mastitis":
            # Subclinical: early rumination drop (-100 to -150 min), mild temp rise (+0.4 to +0.8)
            # Clinical: temp spike (+1.2 to +2.0°C), rumination down -200 min, feeding down -80 min
            d_temp = progress * 1.8
            d_rum = -progress * 220.0
            d_feed = -progress * 90.0
            d_act = -progress * 25.0

        elif condition == "FMD":
            # Highly acute: severe hyperthermia up to +2.6°C, severe activity drop due to hoof lesions
            d_temp = progress * 2.5
            d_rum = -progress * 300.0
            d_feed = -progress * 180.0
            d_act = -progress * 65.0

        elif condition == "LSD":
            # Biphasic fever (+1.8°C), lethargy, rumination drop
            d_temp = progress * 1.9
            d_rum = -progress * 180.0
            d_feed = -progress * 110.0
            d_act = -progress * 45.0

        elif condition == "BRD":
            # Respiratory fever (+1.6°C), cough/lethargy, activity drop
            d_temp = progress * 1.7
            d_rum = -progress * 190.0
            d_feed = -progress * 100.0
            d_act = -progress * 40.0

        elif condition == "Ketosis":
            # Sub-normal or normal temp, steep rumination collapse (-260 min), low feeding
            d_temp = -progress * 0.4
            d_rum = -progress * 270.0
            d_feed = -progress * 140.0
            d_act = -progress * 35.0

        else:
            return 0.0, 0.0, 0.0, 0.0

        return d_temp, d_rum, d_feed, d_act


if __name__ == "__main__":
    sim = DiseaseProgressionSimulator(seed=101)
    cow = AnimalProfile(
        animal_id="MAH-PUN-042",
        tag_number="TAG-9042",
        breed="Gir-HF Cross",
        age_years=4.5,
        lactation_stage_days=85
    )
    timeline = sim.simulate_animal_timeline(cow, condition="Mastitis", days=14)
    print(f"Generated {len(timeline)} readings for {cow.animal_id}")
    print(f"Sample at Day 0: {timeline[0]}")
    print(f"Sample at Day 9 (Subclinical): {timeline[9 * 24]}")
    print(f"Sample at Day 13 (Clinical): {timeline[13 * 24]}")
