from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEMO_PATH = ROOT / "data" / "sample" / "synthetic_demo.csv"

REQUIRED_COLUMNS = {
    "timestamp_s", "speed_kmh", "obstacle_distance_m",
    "longitudinal_accel_mps2", "brake_active", "scenario"
}

def validate_columns(df: pd.DataFrame) -> None:
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

def load_demo_data() -> pd.DataFrame:
    df = pd.read_csv(DEMO_PATH)
    validate_columns(df)
    return df

def load_real_data(path: str | Path | None = None) -> pd.DataFrame:
    path = Path(path) if path else ROOT / "data" / "processed" / "real_driving_data.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"Real dataset not found at {path}. Inspect and preprocess a licensed source dataset first."
        )
    df = pd.read_csv(path)
    validate_columns(df)
    return df
