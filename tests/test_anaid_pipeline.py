import pandas as pd
from src.anaid_pipeline import mark_future_evasion, add_past_only_features

def test_future_event_label_uses_event_start():
    telemetry = pd.DataFrame({
        "run_id": ["run1"] * 5,
        "timestamp_sec": [0.0, 0.5, 1.0, 1.5, 2.0],
        "speed_mps": [1, 2, 3, 4, 5],
    })
    annotations = pd.DataFrame({"start_sec": [1.4], "end_sec": [2.2]})
    out = mark_future_evasion(telemetry, annotations, horizon_sec=1.0)
    assert out["evasion_within_horizon"].tolist() == [0, 1, 1, 0, 0]

def test_past_features_are_grouped_by_run():
    df = pd.DataFrame({
        "run_id": ["A", "A", "B", "B"],
        "timestamp_sec": [0.0, 1.0, 0.0, 1.0],
        "speed_mps": [10, 20, 100, 110],
    })
    out = add_past_only_features(df, rolling_window_sec=2.0)
    # First row of each drive has no prior sample for rolling std/mean with min_periods=2.
    assert pd.isna(out.loc[0, "speed_mps_past_mean"])
    assert pd.isna(out.loc[2, "speed_mps_past_mean"])
    assert out.loc[1, "speed_mps_past_mean"] == 15
    assert out.loc[3, "speed_mps_past_mean"] == 105
