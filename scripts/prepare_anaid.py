"""Build a model-ready table from normalized per-run telemetry and annotations.

Folder convention:
data/anaid/normalized/run1_telemetry.csv
data/anaid/normalized/run1_annotations.csv
... repeat for run2, run3, run4.

Telemetry CSV must contain timestamp_sec and source signal columns (vEgo, aEgo,
brake, gas, yawRate, leftBlinker, rightBlinker). Annotation CSV must contain
start_sec,end_sec in the same run-relative seconds.
"""
from pathlib import Path
import pandas as pd
from src.anaid_pipeline import normalize_telemetry, build_model_table

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "anaid" / "normalized"
OUTPUT = ROOT / "data" / "processed" / "anaid_model_table.csv"
RUNS = ["run1", "run2", "run3", "run4"]
HORIZON_SEC = 1.0
ROLLING_WINDOW_SEC = 2.0

def main():
    tables = []
    for run_id in RUNS:
        telemetry_path = INPUT / f"{run_id}_telemetry.csv"
        annotation_path = INPUT / f"{run_id}_annotations.csv"
        if not telemetry_path.exists() or not annotation_path.exists():
            raise FileNotFoundError(
                f"Missing {telemetry_path.name} or {annotation_path.name}. "
                "See DATASET_SETUP.md for how to prepare the normalized files."
            )
        raw = pd.read_csv(telemetry_path)
        annotations = pd.read_csv(annotation_path)
        telemetry = normalize_telemetry(raw, run_id=run_id)
        tables.append(build_model_table(
            telemetry, annotations,
            horizon_sec=HORIZON_SEC,
            rolling_window_sec=ROLLING_WINDOW_SEC,
        ))
    result = pd.concat(tables, ignore_index=True)
    if result["evasion_within_horizon"].nunique() < 2:
        raise ValueError("Prepared target has only one class; inspect annotations and horizon.")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT, index=False)
    print(f"Saved {len(result):,} rows to {OUTPUT}")
    print(result["evasion_within_horizon"].value_counts(dropna=False))
    print("Runs:", sorted(result["run_id"].unique()))

if __name__ == "__main__":
    main()
