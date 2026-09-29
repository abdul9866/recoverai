import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, HistGradientBoostingClassifier, StackingClassifier
from xgboost import XGBClassifier, XGBRegressor

from common.config import DATASET_DIR, MODEL_PATH
from predictor.features import FS_ENCODING, MEDIUM_ENCODING, ALLOC_ENCODING, CAT_ENCODING, FEATURE_NAMES

def load_dataset():
    csv_path = DATASET_DIR / "recoverability_dataset.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Dataset not found at {csv_path}. Run generate_deletions.py first.")

    df = pd.read_csv(csv_path)

    df["filesystem_num"] = df["filesystem"].map(lambda x: FS_ENCODING.get(str(x), 0))
    df["medium_num"] = df["medium"].map(lambda x: MEDIUM_ENCODING.get(str(x), 0))
    df["log_elapsed_s"] = df["delay_s"].apply(lambda x: np.log1p(max(0.0, float(x))))
    df["disk_usage_pct"] = df["usage_pct"].astype(float)
    df["log_size_bytes"] = df["size_bytes"].apply(lambda x: np.log1p(max(0.0, float(x))))
    df["alloc_num"] = df["allocation_state"].map(lambda x: ALLOC_ENCODING.get(str(x), 1))
    df["cat_num"] = df["file_category"].map(lambda x: CAT_ENCODING.get(str(x).lower(), 1))

    # High-expressivity interaction features
    df["medium_x_delay"] = df["medium_num"] * df["log_elapsed_s"]
    df["usage_x_delay"] = df["disk_usage_pct"] * df["log_elapsed_s"]
    df["size_x_usage"] = df["log_size_bytes"] * df["disk_usage_pct"]
    df["is_ssd_trim"] = (df["medium"] == "SSD_TRIM_ON").astype(float)
    df["delay_sq"] = df["log_elapsed_s"] ** 2
    df["usage_sq"] = df["disk_usage_pct"] ** 2

    label_map = {"none": 0, "partial": 1, "full": 2}
    df["label_num"] = df["label"].map(label_map).fillna(0).astype(int)

    if "actual_fraction" not in df.columns:
        df["actual_fraction"] = df["label_num"] / 2.0

    return df

def train_models():
    df = load_dataset()

    feature_cols = [
        "filesystem_num", "medium_num", "log_elapsed_s", "disk_usage_pct",
        "log_size_bytes", "alloc_num", "cat_num",
        "medium_x_delay", "usage_x_delay", "size_x_usage",
        "is_ssd_trim", "delay_sq", "usage_sq"
    ]

    X = df[feature_cols]
    y_class = df["label_num"]
    y_frac = df["actual_fraction"].astype(float)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_class, test_size=0.2, random_state=42, stratify=y_class
    )
    _, _, y_frac_train, y_frac_test = train_test_split(
        X, y_frac, test_size=0.2, random_state=42, stratify=y_class
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 1. Baseline Logistic Regression
    baseline = LogisticRegression(max_iter=2000, C=2.0)
    baseline.fit(X_train_scaled, y_train)
    baseline_acc = baseline.score(X_test_scaled, y_test)

    # 2. Tuned XGBoost Classifier
    xgb_clf = XGBClassifier(
        n_estimators=400,
        max_depth=5,
        learning_rate=0.03,
        subsample=0.9,
        colsample_bytree=0.9,
        eval_metric="mlogloss",
        random_state=42
    )
    xgb_clf.fit(X_train, y_train)
    xgb_acc = xgb_clf.score(X_test, y_test)

    # 3. Optimized Random Forest
    rf_clf = RandomForestClassifier(
        n_estimators=400,
        max_depth=10,
        min_samples_split=2,
        random_state=42
    )
    rf_clf.fit(X_train, y_train)
    rf_acc = rf_clf.score(X_test, y_test)

    # 4. Stacking Meta-Learner (Base: RF + XGB + LogisticReg -> Meta: LogisticReg)
    stacking_clf = StackingClassifier(
        estimators=[
            ("rf", rf_clf),
            ("xgb", xgb_clf),
            ("lr", baseline)
        ],
        final_estimator=LogisticRegression(C=1.0, max_iter=1000),
        passthrough=True
    )
    stacking_clf.fit(X_train_scaled, y_train)
    stacking_acc = stacking_clf.score(X_test_scaled, y_test)

    print(f"\n================ RECOVERAI MODEL ACCURACY SUMMARY ================")
    print(f"1. Baseline Logistic Regression: {baseline_acc * 100:.2f}%")
    print(f"2. XGBoost Classifier:           {xgb_acc * 100:.2f}%")
    print(f"3. Random Forest Classifier:     {rf_acc * 100:.2f}%")
    print(f"------------------------------------------------------------------")
    print(f"--> STACKING META-ENSEMBLE ACCURACY: {stacking_acc * 100:.2f}% <--")
    print(f"==================================================================\n")

    # XGBoost Regressor for expected byte fraction [0, 1]
    xgb_reg = XGBRegressor(
        n_estimators=400,
        max_depth=5,
        learning_rate=0.03,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42
    )
    xgb_reg.fit(X_train, y_frac_train)
    r2_score = xgb_reg.score(X_test, y_frac_test)
    print(f"XGBoost Regressor R^2 Score: {r2_score:.4f}")

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    bundle = {
        "classifier": stacking_clf,
        "scaler": scaler,
        "xgb_classifier": xgb_clf,
        "regressor": xgb_reg,
        "baseline": baseline,
        "feature_names": FEATURE_NAMES,
        "metrics": {
            "baseline_accuracy": baseline_acc,
            "xgb_accuracy": xgb_acc,
            "rf_accuracy": rf_acc,
            "ensemble_accuracy": stacking_acc,
            "xgb_r2": r2_score
        }
    }
    joblib.dump(bundle, MODEL_PATH)
    print(f"Saved optimized stacking model bundle to {MODEL_PATH}")
    return bundle

if __name__ == "__main__":
    train_models()
