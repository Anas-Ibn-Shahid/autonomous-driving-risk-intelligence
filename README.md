# Autonomous Driving Risk Intelligence

**An exploratory machine-learning project for analysing driving telemetry and forecasting the onset of annotated evasive manoeuvres.**

[![Python](https://img.shields.io/badge/python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/demo-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Tests](https://img.shields.io/badge/tests-pytest-0A9EDC?logo=pytest&logoColor=white)](https://docs.pytest.org/)

> **Status — research prototype.** The dashboard currently runs on synthetic demonstration data. The ANAID preprocessing and model-training workflow is implemented, but it has not yet been evaluated on the real dataset. No real-world model-performance claims are made.

## Project overview

This project explores an early-warning behavioural classification task using naturalistic driving telemetry. It is designed to investigate whether current and recent non-steering vehicle signals contain information about the near-future onset of an annotated evasive manoeuvre.

The repository contains two deliberately separate workflows:

1. **Interactive demo:** a Streamlit dashboard that explores a small synthetic dataset and demonstrates the data-analysis interface.
2. **Real-data research pipeline:** utilities to normalize per-drive telemetry, create a future-event label, engineer past-only features, and evaluate a classifier using drive-session holdouts.

## Research question

**Will an annotated evasive manoeuvre start within the next 1.0 second?**

The pipeline labels a telemetry row positive when an annotation's `start_sec` falls in the interval `(t, t + 1.0]`. Features are built from current and trailing telemetry over a nominal two-second window. Steering angle, steering rate, and steering torque are intentionally excluded from predictors because the source annotations are derived from steering behaviour; this is intended to reduce direct target leakage.

This is a narrowly defined **behavioural event-onset forecasting** experiment. An evasive manoeuvre is not synonymous with a collision, near-crash, or confirmed hazard.

## Key components

| Component | Purpose |
|---|---|
| `app.py` | Streamlit dashboard for the synthetic demo dataset |
| `src/anaid_pipeline.py` | Telemetry normalization, target construction, and past-only feature engineering |
| `scripts/prepare_anaid.py` | Builds the normalized multi-run model table |
| `src/train.py` | Random Forest training and Leave-One-Drive-Out evaluation |
| `tests/` | Unit tests for selected feature and preprocessing behaviour |
| `DATASET_SETUP.md` | Dataset preparation contract, methodology, and limitations |

## Repository structure

```text
autonomous-driving-risk-intelligence/
├── .github/workflows/tests.yml
├── app.py
├── data/
│   ├── sample/synthetic_demo.csv
│   ├── raw/                 # local source files; not committed
│   └── processed/           # generated tables; not committed
├── models/                  # generated model artifacts; not committed
├── scripts/
│   └── prepare_anaid.py
├── src/
│   ├── anaid_pipeline.py
│   ├── analysis.py
│   ├── data.py
│   ├── features.py
│   └── train.py
├── tests/
├── DATASET_SETUP.md
├── requirements.txt
└── README.md
```

## Upload this project to GitHub

This repository is prepared for the public GitHub repository configured in `publish_to_github.bat`:

`https://github.com/Anas-Ibn-Shahid/autonomous-driving-risk-intelligence`

On Windows, install [Git for Windows](https://git-scm.com/download/win), extract the project ZIP, then double-click `publish_to_github.bat` from the extracted project folder. The script initializes Git, stages the project files, creates a commit, and pushes the `main` branch. On the first push, Git may open a browser window for GitHub sign-in. See [`UPLOAD_TO_GITHUB.md`](UPLOAD_TO_GITHUB.md) for step-by-step instructions and troubleshooting.

Do not add raw/private datasets, passwords, access tokens, or generated model files to the repository. The `.gitignore` excludes the configured local data and model-output folders.

## Quick start — Windows / Anaconda

Open **Anaconda Prompt** in the project folder and run:

```bash
conda create -n av-risk python=3.11 -y
conda activate av-risk
pip install -r requirements.txt
streamlit run app.py
```

The dashboard opens in your browser. It displays **synthetic demo data only**; the sample is artificial and is included to test the dashboard and analysis flow.

## Real-data workflow — ANAID

The model workflow is designed around the **Autonomous Naturalistic Obstacle-Avoidance Interaction Dataset (ANAID)**. Before using it, read [`DATASET_SETUP.md`](DATASET_SETUP.md), inspect the exact downloaded release, and verify its timestamps, units, sampling rate, signal names, synchronization, and licence.

References:

- [ANAID dataset record on Zenodo](https://zenodo.org/records/18845673)
- [ANAID companion repository](https://github.com/mgarciafernandez-uem/ANAID)
- [Dataset paper](https://www.mdpi.com/2306-5729/11/4/77)

The raw dataset is **not included** in this repository. Prepare the eight run-specific normalized CSV files described in `DATASET_SETUP.md`, then execute:

```bash
python scripts/prepare_anaid.py
python -m src.train
```

The feature builder currently translates a nominal two-second window into a row-count window using an approximately 2 Hz sampling assumption. **Verify the actual sampling frequency and resample irregular telemetry before relying on these features.** Do not infer source schema or units from the starter code alone.

## Evaluation approach

The training scaffold uses **Leave-One-Drive-Out** validation: each fold holds out one complete drive session rather than randomly splitting adjacent time-series rows. It reports fold-level and pooled metrics including precision, recall, F1, average precision, and a confusion matrix; ROC-AUC is included when both classes are present in the evaluated data. Folds with a single class are skipped with a message.

ANAID has only a small number of independent drive sessions. Consequently, performance estimates may be unstable and are not evidence of generalization to other drivers, vehicles, road conditions, or deployment environments. Inspect false positives and false negatives and compare against a simple baseline before drawing conclusions.

## Run tests

```bash
python -m pytest -q
```

Unit tests validate selected code paths only. They do **not** validate the data mapping, real-world predictive performance, or safety of the system.

## Limitations and responsible use

- The included dashboard data are synthetic, not recorded vehicle telemetry.
- The real ANAID files must be obtained, inspected, normalized, and kept synchronized by drive session.
- The event target represents annotated evasive-manoeuvre onset, not collision or crash risk.
- The two-second feature window currently relies on an approximately 2 Hz assumption; confirm or adapt it to the actual data frequency.
- The number of independent sessions is small, limiting statistical confidence and generalizability.
- This is an educational/research portfolio prototype, **not** a production driver-assistance system, an autonomous-driving stack, or a safety-certified component.

## Roadmap

- [ ] Inspect and document the raw ANAID release and exact signal schema.
- [ ] Verify timestamps, units, synchronization, and sampling frequency.
- [ ] Prepare the four run-specific normalized telemetry/annotation pairs.
- [ ] Run real-data preprocessing and inspect label balance per session.
- [ ] Train, evaluate, and compare against a simple baseline.
- [ ] Document fold-level results, failure cases, and limitations.
- [ ] Connect real-data outputs to the dashboard with clear provenance labels.

## Author

**Anas Ibn Shahid**  
Data Science · Machine Learning · Autonomous Systems

---

*Built as an exploratory portfolio project. Experimental outputs should not be used to make real-world driving or safety decisions.*
