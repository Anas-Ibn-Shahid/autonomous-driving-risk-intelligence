"""ANAID preprocessing and leakage-aware event prediction utilities.

Expected normalized inputs:
- One telemetry CSV per drive/session with a timestamp in seconds and raw ANAID signals.
- One annotations CSV per drive/session with start_sec and end_sec columns.
The source dataset's raw column names may vary by release; map them explicitly in config.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

DEFAULT_SIGNAL_MAP = {
    "vEgo": "speed_mps",
    "aEgo": "accel_mps2",
    "brake": "brake",
    "gas": "gas",
    "yawRate": "yaw_rate",
    "leftBlinker": "left_blinker",
    "rightBlinker": "right_blinker",
}

def normalize_telemetry(
    df: pd.DataFrame,
    run_id: str,
    timestamp_col: str = "timestamp_sec",
    signal_map: dict[str, str] | None = None,
) -> pd.DataFrame:
    """Normalize source telemetry names; timestamp must already be seconds."""
    signal_map = signal_map or DEFAULT_SIGNAL_MAP
    if timestamp_col not in df.columns:
        raise ValueError(
            f"Missing '{timestamp_col}'. Convert the source timestamp to seconds "
            "relative to the start of this drive before calling normalize_telemetry."
        )
    out = pd.DataFrame({"timestamp_sec": pd.to_numeric(df[timestamp_col], errors="coerce")})
    for source_col, target_col in signal_map.items():
        if source_col in df.columns:
            out[target_col] = pd.to_numeric(df[source_col], errors="coerce")
    out["run_id"] = str(run_id)
    out = out.dropna(subset=["timestamp_sec"]).sort_values("timestamp_sec")
    out = out.drop_duplicates(subset=["timestamp_sec"]).reset_index(drop=True)
    if out.empty:
        raise ValueError(f"No valid telemetry rows for run {run_id}.")
    return out

def mark_future_evasion(
    telemetry: pd.DataFrame,
    annotations: pd.DataFrame,
    horizon_sec: float = 1.0,
) -> pd.DataFrame:
    """Label a row positive if an annotated evasion STARTS within (t, t+horizon].

    Labels use event start times only. Telemetry features are constructed from
    current/past signals; steering angle/rate/torque are deliberately excluded
    because the source evasion annotations are themselves derived from steering.
    """
    required = {"start_sec", "end_sec"}
    missing = required.difference(annotations.columns)
    if missing:
        raise ValueError(f"Annotations need columns: {sorted(required)}")
    starts = pd.to_numeric(annotations["start_sec"], errors="coerce").dropna().to_numpy()
    out = telemetry.copy()
    t = out["timestamp_sec"].to_numpy(dtype=float)
    labels = np.zeros(len(out), dtype=np.int8)
    if len(starts):
        starts = np.sort(starts)
        # first event start strictly after t; positive when no more than horizon away
        next_idx = np.searchsorted(starts, t, side="right")
        valid = next_idx < len(starts)
        next_start = np.full(len(t), np.inf)
        next_start[valid] = starts[next_idx[valid]]
        labels[(next_start > t) & (next_start <= t + horizon_sec)] = 1
    out["evasion_within_horizon"] = labels
    return out

def add_past_only_features(
    df: pd.DataFrame,
    rolling_window_sec: float = 2.0,
) -> pd.DataFrame:
    """Create current and trailing-window features without using future rows."""
    out = df.sort_values(["run_id", "timestamp_sec"]).copy()
    numeric = [
        c for c in [
            "speed_mps", "accel_mps2", "brake", "gas", "yaw_rate",
            "left_blinker", "right_blinker"
        ] if c in out.columns
    ]
    if not numeric:
        raise ValueError("No supported telemetry signals found after column mapping.")
    for col in numeric:
        out[f"{col}_current"] = out[col]
        # Rolling means/std use current and prior observations only.
        # ANAID telemetry is described as approximately 2 Hz. Convert the
        # trailing time window to a row window; this avoids pandas time-window
        # requirements on numeric timestamps. For irregular data, resample first.
        rows_per_window = max(2, int(round(rolling_window_sec * 2)))
        grouped = out.groupby("run_id", sort=False)[col]
        for stat in ("mean", "std"):
            rolled = grouped.transform(
                lambda series: getattr(
                    series.rolling(window=rows_per_window, min_periods=2), stat
                )()
            )
            out[f"{col}_past_{stat}"] = rolled
    return out

def build_model_table(
    telemetry: pd.DataFrame,
    annotations: pd.DataFrame,
    horizon_sec: float = 1.0,
    rolling_window_sec: float = 2.0,
) -> pd.DataFrame:
    labelled = mark_future_evasion(telemetry, annotations, horizon_sec)
    featured = add_past_only_features(labelled, rolling_window_sec)
    feature_cols = [
        c for c in featured.columns
        if c.endswith("_current") or c.endswith("_past_mean") or c.endswith("_past_std")
    ]
    keep = ["run_id", "timestamp_sec", "evasion_within_horizon"] + feature_cols
    result = featured[keep].replace([np.inf, -np.inf], np.nan)
    result = result.dropna(subset=feature_cols, how="all")
    return result
