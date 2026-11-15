import pandas as pd
from src.features import add_temporal_features

def test_differences_are_calculated():
    df = pd.DataFrame({
        "timestamp_s": [1, 2, 3],
        "speed_kmh": [10, 20, 25],
        "obstacle_distance_m": [12, 8, 6],
        "longitudinal_accel_mps2": [0.0, 1.0, 0.5],
        "brake_active": [0, 0, 1],
        "scenario": ["urban", "urban", "urban"],
    })
    out = add_temporal_features(df)
    assert pd.isna(out.loc[0, "distance_change_m"])
    assert out["distance_change_m"].iloc[1:].tolist() == [-4, -2]
    assert out["speed_change_kmh"].iloc[1:].tolist() == [10, 5]

def test_differences_do_not_cross_drive_boundaries():
    df = pd.DataFrame({
        "drive_id": ["A", "A", "B", "B"],
        "timestamp_s": [1, 2, 1, 2],
        "speed_kmh": [10, 12, 80, 81],
        "obstacle_distance_m": [20, 18, 5, 4],
        "longitudinal_accel_mps2": [0, 1, 0, 1],
        "brake_active": [0, 0, 1, 1],
        "scenario": ["urban"] * 4,
    })
    out = add_temporal_features(df, sequence_col="drive_id")
    assert pd.isna(out.loc[0, "distance_change_m"])
    assert pd.isna(out.loc[2, "distance_change_m"])
