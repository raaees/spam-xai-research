# Spam Account Detection using XAI (SHAP)

A modular research codebase for explainable machine learning in social network spam detection.

## Project goal

This project implements a research pipeline for detecting malicious/spam accounts in social networks using a multimodal and interpretable approach with:

- behavioral/profile features
- textual features using BERT
- graph representations using PyG
- dynamic multimodal fusion
- final XGBoost classifier with TreeSHAP explanations

## Main dataset

The primary dataset is Cresci-2017.

Important research rules:
- Genuine accounts are class 0.
- Traditional spambots and social spambots are class 1.
- Fake followers are excluded from the main experiment.
- The implementation must inspect the actual dataset schema before assuming columns or graph structure.

## Phase 1 status

Implemented and validated:
- dataset file discovery
- CSV/JSON schema inspection
- automatic detection of account/tweet/text/timestamp/label columns
- duplicate and missing-value checks
- binary label mapping
- saveable schema report

## Repository structure

```text
spam_xai/
├── configs/
│   └── config.yaml
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
├── src/
│   ├── data/
│   ├── features/
│   ├── models/
│   ├── explainability/
│   ├── evaluation/
│   └── utils/
├── scripts/
│   └── 01_validate_data.py
├── tests/
├── outputs/
├── requirements.txt
├── README.md
├── run_pipeline.py
└── .gitignore
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Data location

Put your Cresci-2017 files under:

```text
data/raw/cresci2017/
```

## Run validation

```bash
python scripts/01_validate_data.py
```

This will inspect the dataset, detect schema, and save a report to:

```text
data/interim/schema_report.json
```

## Notes

- The code fails gracefully if required fields are missing.
- No assumptions are made about the dataset before inspection.
- Graph construction is not fabricated; it depends on the actual schema.

---

Research project for explainable spam-account detection.
