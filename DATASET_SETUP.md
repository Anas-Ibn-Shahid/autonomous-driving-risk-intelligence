# ANAID dataset setup for this project

## Source and scope

This project uses ANAID, a real naturalistic driving dataset. The paper describes four independent continuous driving campaigns, telemetry signals from the vehicle `carState` message, and event annotations for evasive manoeuvres. The authors state that the dataset is openly available under CC BY 4.0. Read and cite the paper and dataset before use:

- Paper: https://www.mdpi.com/2306-5729/11/4/77
- Zenodo: https://zenodo.org/records/18845673
- Companion preprocessing repository: https://github.com/mgarciafernandez-uem/ANAID

The paper describes the raw `carState` timestamp `t` in nanoseconds and signals including `vEgo` (m/s), `aEgo` (m/s²), `gas`, `brake`, `yawRate`, `leftBlinker`, and `rightBlinker`. The repository's analysis code emits event summaries with `t_start` and `t_end` in recording-relative seconds. Verify the actual downloaded release and its column names before mapping them.

## Normalized input files expected by this starter

Create `data/anaid/normalized/` and place these eight files there:

- `run1_telemetry.csv` ... `run4_telemetry.csv`
- `run1_annotations.csv` ... `run4_annotations.csv`

Each telemetry CSV must have:
- `timestamp_sec`: time in seconds relative to the start of that run, increasing within the run
- `vEgo`, `aEgo`, `brake`, `gas`, `yawRate`, `leftBlinker`, `rightBlinker` (include only columns actually present in the downloaded source; the default feature builder uses those available)

Each annotation CSV must have:
- `start_sec`: start time of an annotated evasive manoeuvre, in the same run-relative seconds
- `end_sec`: end time of the same manoeuvre

Do not mix timestamps from separate chunks without applying the dataset's synchronization/unification procedure. Do not merge events from a different run. Do not guess column mappings or units. If the release contains per-chunk annotation files, consolidate them only after confirming their time bases and offsets.

## Prediction task

The model predicts whether an annotated evasive manoeuvre will START within the next 1.0 second, using only current and trailing 2-second summaries of non-steering telemetry. Steering angle, steering rate, and steering torque are excluded from predictors because the published annotation method derives evasive manoeuvre labels from steering-related signals. This reduces direct target leakage.

This is a behavioural early-warning experiment, not a collision-risk detector and not a certified safety system. An evasive manoeuvre is not synonymous with a crash or near-crash.

## Run

```bash
python scripts/prepare_anaid.py
python -m src.train
```

The training script uses Leave-One-Drive-Out evaluation so each test fold is a separate drive session. ANAID has only four campaigns/drivers, so results have substantial uncertainty and limited generalizability. Report this limitation prominently. Do not present a single score as evidence of deployment readiness.

## Important methodology cautions

- The target is derived from the dataset's published evasive-manoeuvre annotations, which themselves are algorithmically detected from steering telemetry and manually reviewed by the authors.
- Predictors intentionally exclude steering-derived variables. Still, check temporal alignment and any data preprocessing carefully.
- The 1-second horizon is a project design choice, not a property guaranteed by the dataset authors.
- Use session-level evaluation; never randomly split adjacent telemetry rows across train/test.
- Compare against a simple baseline and inspect false positives/false negatives before claiming usefulness.
- If a run has no positive examples or no negative examples in a held-out fold, that fold cannot produce a valid binary classification report and is skipped with an explicit message.
