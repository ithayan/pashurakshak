"""
PashuRakshak Digital Twin - Surrogate Model Trainer & ONNX Exporter
==================================================================
Trains a multi-task neural network on the simulator-generated synthetic data.
Predicts:
1. Disease classification probabilities: Healthy, Mastitis, FMD, LSD, BRD, Ketosis
2. Days-to-symptom early warning estimate (e.g. 2.4 days before clinical manifestation)

Exports model to ONNX for low-latency (<5ms) edge/cloud inference in AI Core.
"""

import os
import sys
import json

# Ensure utf-8 encoding for Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import pandas as pd
import numpy as np
import onnx
import onnxruntime as ort

FEATURE_COLS = [
    "temperature",
    "temp_24h_delta",
    "temp_24h_mean",
    "rumination_minutes",
    "rumination_drop_pct",
    "feeding_minutes",
    "feeding_drop_pct",
    "activity_index",
    "activity_drop_pct"
]

CLASSES = ["Healthy", "Mastitis", "FMD", "LSD", "BRD", "Ketosis"]
CLASS_TO_IDX = {c: i for i, c in enumerate(CLASSES)}


class LivestockHealthSurrogate(nn.Module):
    """Multi-task neural network surrogate for livestock health."""

    def __init__(self, in_features: int = 9, num_classes: int = 6):
        super().__init__()
        self.shared = nn.Sequential(
            nn.Linear(in_features, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.15),
            nn.Linear(64, 32),
            nn.BatchNorm1d(32),
            nn.ReLU()
        )
        # Classification head (disease state)
        self.classifier = nn.Linear(32, num_classes)
        # Regression head (days until overt clinical signs)
        self.regressor = nn.Sequential(
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1)
        )

    def forward(self, x):
        features = self.shared(x)
        logits = self.classifier(features)
        probs = torch.softmax(logits, dim=1)
        days = self.regressor(features)
        return probs, days


def train_and_export(
    data_path: str = "data/synthetic_cattle_cohorts.csv",
    export_dir: str = "models",
    epochs: int = 35,
    batch_size: int = 64
):
    os.makedirs(export_dir, exist_ok=True)
    df = pd.read_csv(data_path)

    X_raw = df[FEATURE_COLS].values.astype(np.float32)
    y_class = np.array([CLASS_TO_IDX[c] for c in df["condition"]], dtype=np.int64)
    y_days = np.clip(df["days_to_symptom"].values.astype(np.float32), 0.0, 5.0).reshape(-1, 1)

    # Compute standardization stats
    means = np.mean(X_raw, axis=0)
    stds = np.std(X_raw, axis=0) + 1e-6
    X_norm = (X_raw - means) / stds

    # Save normalization metadata for AI Core
    norm_meta = {
        "features": FEATURE_COLS,
        "means": means.tolist(),
        "stds": stds.tolist(),
        "classes": CLASSES,
        "class_to_idx": CLASS_TO_IDX
    }
    meta_path = os.path.join(export_dir, "model_metadata.json")
    with open(meta_path, "w") as f:
        json.dump(norm_meta, f, indent=2)
    print(f"Saved normalization metadata to {meta_path}")

    # Train / Val split (80/20)
    indices = np.random.permutation(len(X_norm))
    split = int(0.8 * len(X_norm))
    train_idx, val_idx = indices[:split], indices[split:]

    train_ds = TensorDataset(
        torch.tensor(X_norm[train_idx]),
        torch.tensor(y_class[train_idx]),
        torch.tensor(y_days[train_idx])
    )
    val_ds = TensorDataset(
        torch.tensor(X_norm[val_idx]),
        torch.tensor(y_class[val_idx]),
        torch.tensor(y_days[val_idx])
    )

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)

    model = LivestockHealthSurrogate(in_features=len(FEATURE_COLS), num_classes=len(CLASSES))
    criterion_cls = nn.CrossEntropyLoss()
    criterion_reg = nn.SmoothL1Loss()
    optimizer = optim.AdamW(model.parameters(), lr=0.003, weight_decay=1e-4)

    print(f"Training surrogate neural network for {epochs} epochs...")
    for epoch in range(epochs):
        model.train()
        total_loss = 0.0
        for bx, by_c, by_d in train_loader:
            optimizer.zero_grad()
            probs, pred_days = model(bx)
            # Logits for cross entropy loss
            logits = torch.log(probs + 1e-8)
            loss_cls = criterion_cls(logits, by_c)
            loss_reg = criterion_reg(pred_days, by_d)
            loss = loss_cls + 0.5 * loss_reg
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        if (epoch + 1) % 5 == 0 or epoch == epochs - 1:
            model.eval()
            correct = 0
            total = 0
            with torch.no_grad():
                for bx, by_c, by_d in val_loader:
                    probs, pred_days = model(bx)
                    preds = torch.argmax(probs, dim=1)
                    correct += (preds == by_c).sum().item()
                    total += len(by_c)
            acc = (correct / total) * 100.0
            print(f"Epoch [{epoch+1:02d}/{epochs:02d}] - Loss: {total_loss/len(train_loader):.4f} - Val Accuracy: {acc:.2f}%")

    # Export to ONNX
    model.eval()
    dummy_input = torch.randn(1, len(FEATURE_COLS), dtype=torch.float32)
    onnx_path = os.path.join(export_dir, "livestock_health_surrogate.onnx")

    torch.onnx.export(
        model,
        dummy_input,
        onnx_path,
        export_params=True,
        opset_version=14,
        do_constant_folding=True,
        input_names=["vital_signs_input"],
        output_names=["disease_probabilities", "days_to_symptom"],
        dynamic_axes={
            "vital_signs_input": {0: "batch_size"},
            "disease_probabilities": {0: "batch_size"},
            "days_to_symptom": {0: "batch_size"}
        },
        dynamo=False
    )
    print(f"Model exported successfully to {onnx_path}")

    # Verify ONNX model with onnxruntime
    ort_session = ort.InferenceSession(onnx_path)
    sample_in = X_norm[:2]
    ort_inputs = {ort_session.get_inputs()[0].name: sample_in}
    ort_outs = ort_session.run(None, ort_inputs)
    print("ONNX verification successful!")
    print("Sample Output Probabilities:\n", np.round(ort_outs[0], 3))
    print("Sample Days-to-symptom estimate:\n", np.round(ort_outs[1], 2))


if __name__ == "__main__":
    train_and_export(
        data_path="C:/Users/91900/.gemini/antigravity-ide/scratch/pashurakshak/digital-twin/data/synthetic_cattle_cohorts.csv",
        export_dir="C:/Users/91900/.gemini/antigravity-ide/scratch/pashurakshak/digital-twin/models",
        epochs=30
    )
