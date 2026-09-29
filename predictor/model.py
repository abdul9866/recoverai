import joblib
import numpy as np
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from common.config import MODEL_PATH
from common.schema import DeletedFileRecord, RecoverabilityPrediction
from predictor.features import to_feature_vector

@dataclass
class CaseAdaptiveModel:
    """
    CARP Component 1: Case-Adaptive Online Model.
    Wraps the offline-trained prior with a per-case online bias term (theta).

    theta starts at 1.0 (no adjustment). Each observed recovery outcome nudges theta
    via an exponential-moving-average (EMA) update, adapting predictions to disk-specific
    aging, TRIM settings, and controller characteristics.
    """
    theta: float = 1.0
    learning_rate: float = 0.15
    model_path: Path = field(default_factory=lambda: MODEL_PATH)
    _bundle: Optional[dict] = field(default=None, repr=False)

    def __post_init__(self):
        if self._bundle is None:
            if self.model_path.exists():
                self._bundle = joblib.load(self.model_path)
            else:
                self._bundle = None

    def predict(self, rec: DeletedFileRecord) -> RecoverabilityPrediction:
        """Computes case-adaptive recoverability predictions for a record."""
        if self._bundle is None or "classifier" not in self._bundle:
            # Heuristic fallback if model file has not been serialized yet
            days = rec.elapsed_seconds_since_delete / 86400.0
            med_str = rec.medium.value if hasattr(rec.medium, "value") else str(rec.medium)
            if med_str == "SSD_TRIM_ON":
                exp_frac = 0.95 if rec.elapsed_seconds_since_delete == 0 else 0.05
            else:
                exp_frac = max(0.05, 0.9 * np.exp(-0.3 * days * (rec.disk_usage_pct_at_delete ** 1.5)))

            adj_exp_frac = float(np.clip(exp_frac * self.theta, 0.0, 1.0))
            return RecoverabilityPrediction(
                file_id=rec.file_id,
                p_full=adj_exp_frac,
                p_partial=max(0.0, (1.0 - adj_exp_frac) * 0.5),
                expected_fraction=adj_exp_frac,
                confidence=float(np.clip(1.0 - abs(1.0 - self.theta), 0.1, 1.0)),
            )

        x = to_feature_vector(rec).reshape(1, -1)
        p_class = self._bundle["classifier"].predict_proba(x)[0]   # [p_none, p_partial, p_full]
        expected_fraction = float(self._bundle["regressor"].predict(x)[0])

        adj_expected_fraction = float(np.clip(expected_fraction * self.theta, 0.0, 1.0))
        p_full_raw = p_class[2] if len(p_class) > 2 else p_class[-1]
        p_partial_raw = p_class[1] if len(p_class) > 1 else 0.0

        adj_p_full = float(np.clip(p_full_raw * self.theta, 0.0, 1.0))
        adj_p_partial = float(np.clip(p_partial_raw * self.theta, 0.0, 1.0))
        confidence = float(np.clip(1.0 - abs(1.0 - self.theta), 0.1, 1.0))

        return RecoverabilityPrediction(
            file_id=rec.file_id,
            p_full=adj_p_full,
            p_partial=adj_p_partial,
            expected_fraction=adj_expected_fraction,
            confidence=confidence,
        )

    def update(self, predicted_fraction: float, actual_fraction: float):
        """
        Updates theta online after observing the real recovery outcome for a file.
        Call this after every real recovery attempt on the current disk.
        """
        if predicted_fraction <= 1e-6:
            return
        observed_ratio = actual_fraction / predicted_fraction
        observed_ratio = float(np.clip(observed_ratio, 0.1, 3.0))   # Guard against wild swings
        self.theta = (1.0 - self.learning_rate) * self.theta + self.learning_rate * observed_ratio
