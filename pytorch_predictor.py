#!/usr/bin/env python3
"""
RecoverAI v2.0 – PyTorch Neural Network Recoverability Predictor
Replaces / complements XGBoost with a 3-class MLP classifier and
a regression head for expected recovery fraction.

Architecture:
    Input: 7 features
    → Linear(7 → 64) → BatchNorm → ReLU → Dropout(0.3)
    → Linear(64 → 32) → BatchNorm → ReLU → Dropout(0.2)
    → [CLF head] Linear(32 → 3)    (none / partial / full)
    → [REG head] Linear(32 → 1)    (expected recovery fraction)

Training: 5-fold OOF with early stopping on val-loss.
"""

import os
import time
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, f1_score, mean_absolute_error,
    mean_squared_error, r2_score, classification_report
)

RANDOM_SEED = 42
torch.manual_seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ─────────────────────────── Model Definition ────────────────────────────────

class RecoverabilityNet(nn.Module):
    """
    Multi-task MLP:
      - Classification head → 3-class softmax (none/partial/full)
      - Regression head    → sigmoid output (expected fraction ∈ [0,1])
    """
    def __init__(self, n_features: int = 7, n_classes: int = 3,
                 hidden1: int = 64, hidden2: int = 32,
                 dropout1: float = 0.30, dropout2: float = 0.20):
        super().__init__()
        self.shared = nn.Sequential(
            nn.Linear(n_features, hidden1),
            nn.BatchNorm1d(hidden1),
            nn.ReLU(),
            nn.Dropout(dropout1),
            nn.Linear(hidden1, hidden2),
            nn.BatchNorm1d(hidden2),
            nn.ReLU(),
            nn.Dropout(dropout2),
        )
        self.clf_head = nn.Linear(hidden2, n_classes)   # logits → CrossEntropy
        self.reg_head = nn.Sequential(
            nn.Linear(hidden2, 1),
            nn.Sigmoid()                                  # output ∈ [0,1]
        )

    def forward(self, x):
        h = self.shared(x)
        logits = self.clf_head(h)
        frac   = self.reg_head(h).squeeze(-1)
        return logits, frac


# ─────────────────────────── Training Helpers ────────────────────────────────

def make_tensors(X, y_cls, y_reg):
    Xt = torch.tensor(X, dtype=torch.float32)
    yc = torch.tensor(y_cls, dtype=torch.long)
    yr = torch.tensor(y_reg, dtype=torch.float32)
    return Xt, yc, yr


def train_one_epoch(model, loader, optimizer, clf_loss_fn, reg_loss_fn,
                    clf_weight=0.7, reg_weight=0.3):
    model.train()
    total_loss = 0.0
    for Xb, yc_b, yr_b in loader:
        Xb, yc_b, yr_b = Xb.to(DEVICE), yc_b.to(DEVICE), yr_b.to(DEVICE)
        optimizer.zero_grad()
        logits, frac = model(Xb)
        loss = clf_weight * clf_loss_fn(logits, yc_b) + reg_weight * reg_loss_fn(frac, yr_b)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * len(Xb)
    return total_loss / len(loader.dataset)


def evaluate(model, loader, clf_loss_fn, reg_loss_fn, clf_weight=0.7, reg_weight=0.3):
    model.eval()
    total_loss = 0.0
    all_logits, all_fracs = [], []
    with torch.no_grad():
        for Xb, yc_b, yr_b in loader:
            Xb, yc_b, yr_b = Xb.to(DEVICE), yc_b.to(DEVICE), yr_b.to(DEVICE)
            logits, frac = model(Xb)
            loss = clf_weight * clf_loss_fn(logits, yc_b) + reg_weight * reg_loss_fn(frac, yr_b)
            total_loss += loss.item() * len(Xb)
            all_logits.append(logits.cpu())
            all_fracs.append(frac.cpu())
    logits_all = torch.cat(all_logits)
    fracs_all  = torch.cat(all_fracs)
    return (total_loss / len(loader.dataset),
            torch.softmax(logits_all, dim=1).numpy(),
            fracs_all.numpy())


# ─────────────────────────── OOF Training ────────────────────────────────────

def train_oof(X: np.ndarray, y_cls: np.ndarray, y_reg: np.ndarray,
              n_folds: int = 5, epochs: int = 80, batch_size: int = 32,
              lr: float = 1e-3, patience: int = 10) -> dict:
    """
    5-Fold OOF training.
    Returns:
        oof_probs     : (N, 3) softmax probabilities
        oof_preds_cls : (N,) predicted class indices
        oof_preds_reg : (N,) predicted recovery fractions
        fold_histories: list of dicts with per-fold train/val loss curves
    """
    print(f"\n[PyTorch] Device: {DEVICE}  |  Folds: {n_folds}  |  Max Epochs: {epochs}")
    print(f"[PyTorch] Dataset: N={len(X)}  |  Features: {X.shape[1]}")

    unique_classes = np.unique(y_cls)
    n_classes = int(unique_classes.max()) + 1

    scaler = StandardScaler()
    X_sc = scaler.fit_transform(X)

    oof_probs     = np.zeros((len(X), n_classes), dtype=np.float32)
    oof_preds_cls = np.zeros(len(X), dtype=np.int64)
    oof_preds_reg = np.zeros(len(X), dtype=np.float32)
    fold_histories = []

    if len(unique_classes) < 2:
        print("[PyTorch] WARNING: Single class present — skipping OOF, using baseline.")
        cls_val = int(unique_classes[0])
        # Always return (N, 3) shaped array to avoid downstream IndexError
        baseline_probs = np.zeros((len(X), 3), dtype=np.float32)
        baseline_probs[:, cls_val] = 1.0
        baseline_cls = np.full(len(X), cls_val, dtype=np.int64)
        baseline_reg = np.full(len(X), float(np.mean(y_reg)), dtype=np.float32)
        return {
            "oof_probs":      baseline_probs,
            "oof_preds_cls":  baseline_cls,
            "oof_preds_reg":  baseline_reg,
            "scaler":         scaler,
            "fold_histories": fold_histories
        }

    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=RANDOM_SEED)
    clf_loss_fn = nn.CrossEntropyLoss()
    reg_loss_fn = nn.MSELoss()

    for fold_idx, (train_idx, val_idx) in enumerate(skf.split(X_sc, y_cls)):
        print(f"\n  ┌── Fold {fold_idx + 1}/{n_folds}  "
              f"train={len(train_idx)}  val={len(val_idx)}")

        X_tr, X_vl = X_sc[train_idx], X_sc[val_idx]
        yc_tr, yc_vl = y_cls[train_idx], y_cls[val_idx]
        yr_tr, yr_vl = y_reg[train_idx], y_reg[val_idx]

        Xtr_t, yc_tr_t, yr_tr_t = make_tensors(X_tr, yc_tr, yr_tr)
        Xvl_t, yc_vl_t, yr_vl_t = make_tensors(X_vl, yc_vl, yr_vl)

        train_ds = TensorDataset(Xtr_t, yc_tr_t, yr_tr_t)
        val_ds   = TensorDataset(Xvl_t, yc_vl_t, yr_vl_t)
        train_ld = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
        val_ld   = DataLoader(val_ds,   batch_size=batch_size, shuffle=False)

        model = RecoverabilityNet(n_features=X.shape[1], n_classes=n_classes).to(DEVICE)
        optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5, factor=0.5)

        best_val_loss = float("inf")
        best_state    = None
        wait          = 0
        train_losses, val_losses = [], []

        for epoch in range(epochs):
            tr_loss = train_one_epoch(model, train_ld, optimizer, clf_loss_fn, reg_loss_fn)
            vl_loss, vl_probs, vl_fracs = evaluate(model, val_ld, clf_loss_fn, reg_loss_fn)
            scheduler.step(vl_loss)
            train_losses.append(tr_loss)
            val_losses.append(vl_loss)

            if vl_loss < best_val_loss - 1e-5:
                best_val_loss = vl_loss
                best_state    = {k: v.clone() for k, v in model.state_dict().items()}
                wait = 0
            else:
                wait += 1
                if wait >= patience:
                    print(f"  │   Early stop at epoch {epoch+1}  best_val={best_val_loss:.4f}")
                    break

        # Load best weights and infer on val set
        model.load_state_dict(best_state)
        _, final_probs, final_fracs = evaluate(model, val_ld, clf_loss_fn, reg_loss_fn)

        oof_probs[val_idx]     = final_probs
        oof_preds_cls[val_idx] = np.argmax(final_probs, axis=1)
        oof_preds_reg[val_idx] = np.clip(final_fracs, 0.0, 1.0)

        fold_acc = accuracy_score(yc_vl, np.argmax(final_probs, axis=1))
        fold_mae = mean_absolute_error(yr_vl, np.clip(final_fracs, 0.0, 1.0))
        print(f"  └── Fold {fold_idx+1} done | val_loss={best_val_loss:.4f} | "
              f"acc={fold_acc:.4f} | MAE={fold_mae:.4f}")

        fold_histories.append({
            "fold": fold_idx + 1,
            "best_val_loss": best_val_loss,
            "train_losses": train_losses,
            "val_losses": val_losses
        })

    return {
        "oof_probs":     oof_probs,
        "oof_preds_cls": oof_preds_cls,
        "oof_preds_reg": oof_preds_reg,
        "scaler":        scaler,
        "fold_histories": fold_histories
    }


# ─────────────────────────── Metrics Report ──────────────────────────────────

def compute_metrics(y_cls, y_reg, oof_probs, oof_preds_cls, oof_preds_reg,
                    label_names=None) -> dict:
    """Compute and print all evaluation metrics."""
    if label_names is None:
        label_names = ["none", "partial", "full"]
    unique = sorted(np.unique(y_cls).tolist())
    names_present = [label_names[i] for i in unique]

    print("\n╔══════════════════════════════════════════════════════╗")
    print("║    PyTorch MLP — Out-of-Fold Evaluation Report      ║")
    print("╠══════════════════════════════════════════════════════╣")

    acc    = accuracy_score(y_cls, oof_preds_cls)
    f1     = f1_score(y_cls, oof_preds_cls, average="weighted", zero_division=0)
    mae    = mean_absolute_error(y_reg, oof_preds_reg)
    rmse   = np.sqrt(mean_squared_error(y_reg, oof_preds_reg))
    r2     = r2_score(y_reg, oof_preds_reg)

    # AUC-ROC (only if >1 class)
    roc_auc = None
    if len(unique) > 1 and oof_probs.shape[1] >= 2:
        from sklearn.metrics import roc_auc_score
        from sklearn.preprocessing import label_binarize
        y_bin = label_binarize(y_cls, classes=unique)
        try:
            roc_auc = roc_auc_score(y_bin, oof_probs[:, unique], multi_class="ovr", average="macro")
        except Exception:
            roc_auc = None

    print(f"║  Classification Accuracy  : {acc:.4f}                ║")
    print(f"║  Weighted F1-Score        : {f1:.4f}                ║")
    if roc_auc is not None:
        print(f"║  Macro AUC-ROC (OvR)      : {roc_auc:.4f}                ║")
    print(f"║  Regressor MAE            : {mae:.4f}                ║")
    print(f"║  Regressor RMSE           : {rmse:.4f}                ║")
    print(f"║  Regressor R² Score       : {r2:.4f}                ║")
    print("╠══════════════════════════════════════════════════════╣")
    print("║  Per-Class Classification Report:                    ║")

    report = classification_report(y_cls, oof_preds_cls,
                                    target_names=names_present, zero_division=0)
    for line in report.strip().split("\n"):
        print(f"║  {line:<52}║")
    print("╚══════════════════════════════════════════════════════╝")

    return {
        "accuracy":    round(acc, 4),
        "f1_weighted": round(f1, 4),
        "roc_auc_ovr": round(roc_auc, 4) if roc_auc else None,
        "mae":         round(mae, 4),
        "rmse":        round(rmse, 4),
        "r2":          round(r2, 4)
    }
