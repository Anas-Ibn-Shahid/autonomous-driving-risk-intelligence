"""Train and evaluate an evasive-maneuver early-warning classifier.

Uses Leave-One-Drive-Out evaluation. No synthetic demo data is accepted.
"""
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.metrics import (
    classification_report, confusion_matrix, average_precision_score,
    roc_auc_score, precision_recall_fscore_support
)

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "anaid_model_table.csv"
MODEL_DIR = ROOT / "models"
TARGET = "evasion_within_horizon"
GROUP = "run_id"

def make_pipeline(feature_cols):
    prep = ColumnTransformer([
        ("numeric", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]), feature_cols)
    ])
    return Pipeline([
        ("preprocess", prep),
        ("classifier", RandomForestClassifier(
            n_estimators=400,
            min_samples_leaf=3,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ))
    ])

def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError("Run `python scripts/prepare_anaid.py` first.")
    df = pd.read_csv(DATA_PATH)
    required = {TARGET, GROUP, "timestamp_sec"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    feature_cols = [
        c for c in df.columns
        if c.endswith("_current") or c.endswith("_past_mean") or c.endswith("_past_std")
    ]
    if not feature_cols:
        raise ValueError("No engineered feature columns found.")
    df = df.dropna(subset=[TARGET, GROUP])
    X = df[feature_cols].apply(pd.to_numeric, errors="coerce")
    y = df[TARGET].astype(int)
    groups = df[GROUP].astype(str)
    if y.nunique() != 2:
        raise ValueError("Target must contain both 0 and 1 classes.")
    if groups.nunique() < 2:
        raise ValueError("Need at least two independent drive sessions.")

    logo = LeaveOneGroupOut()
    oof_pred = np.zeros(len(df), dtype=int)
    oof_prob = np.zeros(len(df), dtype=float)
    fold_results = []
    for fold, (train_idx, test_idx) in enumerate(logo.split(X, y, groups), start=1):
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        if y_train.nunique() < 2 or y_test.nunique() < 2:
            print(f"Skipping fold {fold}: train or held-out run has only one class.")
            continue
        model = make_pipeline(feature_cols)
        model.fit(X.iloc[train_idx], y_train)
        oof_pred[test_idx] = model.predict(X.iloc[test_idx])
        oof_prob[test_idx] = model.predict_proba(X.iloc[test_idx])[:, 1]
        p, r, f1, _ = precision_recall_fscore_support(
            y_test, oof_pred[test_idx], average="binary", zero_division=0
        )
        fold_results.append({
            "held_out_run": str(groups.iloc[test_idx].iloc[0]),
            "precision": float(p), "recall": float(r), "f1": float(f1),
            "average_precision": float(average_precision_score(y_test, oof_prob[test_idx])),
        })

    evaluated = np.zeros(len(df), dtype=bool)
    for result in fold_results:
        evaluated |= groups.eq(result["held_out_run"]).to_numpy()
    if not evaluated.any():
        raise ValueError("No valid evaluation folds. Check event labels per run.")

    y_eval = y.iloc[evaluated]
    pred_eval = oof_pred[evaluated]
    prob_eval = oof_prob[evaluated]
    metrics = {
        "evaluation": "Leave-One-Drive-Out; metrics pooled over valid held-out drives",
        "rows_evaluated": int(evaluated.sum()),
        "drives": sorted(groups[evaluated].unique().tolist()),
        "positive_rate": float(y_eval.mean()),
        "precision": float(precision_recall_fscore_support(y_eval, pred_eval, average="binary", zero_division=0)[0]),
        "recall": float(precision_recall_fscore_support(y_eval, pred_eval, average="binary", zero_division=0)[1]),
        "f1": float(precision_recall_fscore_support(y_eval, pred_eval, average="binary", zero_division=0)[2]),
        "average_precision": float(average_precision_score(y_eval, prob_eval)),
        "confusion_matrix": confusion_matrix(y_eval, pred_eval).tolist(),
        "folds": fold_results,
    }
    if y_eval.nunique() == 2:
        metrics["roc_auc"] = float(roc_auc_score(y_eval, prob_eval))
    print(json.dumps(metrics, indent=2))
    print("\nClassification report:\n", classification_report(y_eval, pred_eval, zero_division=0))

    # Refit final model on all available sessions only after CV evaluation.
    final_model = make_pipeline(feature_cols)
    final_model.fit(X, y)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": final_model, "feature_columns": feature_cols,
                 "target": TARGET, "horizon_sec": 1.0}, MODEL_DIR / "anaid_evasion_model.joblib")
    (MODEL_DIR / "evaluation_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"\nSaved final model and metrics in {MODEL_DIR}")

if __name__ == "__main__":
    main()
