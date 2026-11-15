import pandas as pd

def add_temporal_features(df: pd.DataFrame, sequence_col: str | None = None) -> pd.DataFrame:
    """Add first differences. For real data, pass sequence_col to prevent crossing trips."""
    out = df.copy()
    sort_cols = ([sequence_col] if sequence_col else []) + ["timestamp_s"]
    out = out.sort_values(sort_cols).reset_index(drop=True)

    if sequence_col:
        grouped = out.groupby(sequence_col, sort=False)
        out["speed_change_kmh"] = grouped["speed_kmh"].diff()
        out["distance_change_m"] = grouped["obstacle_distance_m"].diff()
        out["accel_change_mps2"] = grouped["longitudinal_accel_mps2"].diff()
    else:
        out["speed_change_kmh"] = out["speed_kmh"].diff()
        out["distance_change_m"] = out["obstacle_distance_m"].diff()
        out["accel_change_mps2"] = out["longitudinal_accel_mps2"].diff()

    return out
