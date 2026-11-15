import pandas as pd

def summary_metrics(df: pd.DataFrame) -> dict:
    return {
        "observations": int(len(df)),
        "mean_speed": float(df["speed_kmh"].mean()),
        "mean_distance": float(df["obstacle_distance_m"].mean()),
        "brake_rate": float(df["brake_active"].mean()),
    }
