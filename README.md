# 🏎️ Beyond Detection: Classifying Ambiguous Track Limit Violations in F1

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)](https://www.python.org/)
[![FastF1](https://img.shields.io/badge/Data-FastF1-red)](https://github.com/theOehrly/Fast-F1)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Research-orange)]()
[![Seasons](https://img.shields.io/badge/Seasons-2018--2025-purple)]()

> A telemetry-based machine learning approach to classifying ambiguous Formula 1 track limit violations — the exact class of case the FIA's own AI system (ECAT) still routes to human stewards.

---

## 📌 Overview

Formula 1's track limit enforcement has been a persistent source of controversy. The FIA's AI-assisted system, **ECAT**, automates most track limit decisions but — by the FIA's own public statements — still relies on human stewards for **complex, ambiguous cases**: incidents where a driver leaves the track but may not have gained a clear advantage.

This repository contains the dataset, code, and results for a study that:

- 🏁 Builds a labeled dataset of **4,254 track limit incidents** across **8 F1 seasons (2018–2025)**
- 📡 Uses only **public telemetry and race control data** — no video, no proprietary FIA data
- 🤖 Trains and compares **5 machine learning models** to distinguish *Clear Violations* from *No Advantage* cases
- 🎯 Achieves an **F1-macro score of 0.887** with a Random Forest classifier on a held-out, race-level test split
- 🔍 Uses **SHAP** to explain what drives the model's predictions
- 🧪 Includes an **ablation study** isolating driving telemetry from session context

---

## 📊 Key Results

| Model | Accuracy | F1 | F1 (macro) |
|---|:---:|:---:|:---:|
| **Random Forest** ⭐ | 0.914 | 0.950 | **0.822** |
| XGBoost | 0.914 | 0.950 | 0.821 |
| SVM | 0.915 | 0.951 | 0.816 |
| Logistic Regression | 0.898 | 0.941 | 0.773 |
| MLP | 0.862 | 0.918 | 0.737 |

*(validation set — Random Forest selected as final model)*

**Final test set (held out, 327 incidents):** Accuracy **0.893** · F1-macro **0.887** · ROC AUC **0.942**

---

## 🗂️ Repository Structure

```
├── data/
│   ├── dataset_ready_for_modeling.csv   # Final modeling-ready dataset (4,254 rows)
│   ├── dataset_phase1_complete.csv      # Labeled incidents before feature engineering
│   └── data_dictionary.md               # Column-by-column description
├── scripts/
│   ├── build_dataset_*.py               # Dataset construction (per season)
│   ├── recover_lap_numbers.py           # Timestamp-based lap recovery
│   ├── phase2_telemetry.py              # Telemetry extraction
│   ├── phase3_features.py               # Feature engineering
│   ├── phase4_models.py                 # Model training & comparison
│   ├── phase5_evaluation.py             # Final test evaluation + SHAP
│   └── ablation_no_session.py           # Ablation study
├── results/
│   ├── confusion_matrix.png
│   ├── roc_curve.png
│   ├── pr_curve.png
│   ├── shap_summary.png
│   ├── shap_bar.png
│   ├── model_comparison.png
│   ├── dataset_by_year.png
│   └── phase4_model_comparison.csv
├── requirements.txt
├── LICENSE
└── README.md
```

---

## 🚀 Reproducing This Work

### 1. Set up the environment

```bash
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux
pip install -r requirements.txt
```

### 2. Build the dataset

```bash
python scripts/build_dataset_2018.py
python scripts/build_dataset_2019.py
# ... repeat for each season, or use build_dataset_2020_2022.py etc.
python scripts/recover_lap_numbers.py
python scripts/finalize_dataset.py
```

> ⚠️ Dataset construction queries the public FastF1 API and is subject to a 500 requests/hour rate limit. Scripts are resume-capable — safe to stop and rerun.

### 3. Extract telemetry & engineer features

```bash
python scripts/phase2_telemetry.py
python scripts/clean_telemetry_features.py
python scripts/phase3_features.py
python scripts/fix_speed_ratio.py
python scripts/finalize_phase3.py
python scripts/remove_preseason.py
```

### 4. Train and evaluate models

```bash
python scripts/phase4_models.py
python scripts/phase5_evaluation.py
python scripts/phase5_all_graphs.py
python scripts/ablation_no_session.py
python scripts/era_breakdown.py
```

### Extending to future seasons

This pipeline works for any season FastF1 supports. To add a new season, copy any `build_dataset_*.py` script and change the `YEAR` variable — no other code changes required.

---

## ⚠️ Known Limitations

- **2018:** No `Clear Violation` incidents — FIA's lap-deletion reporting for track limits was not yet consistently applied.
- **2025:** Fewer `No Advantage` incidents detected — FIA's race control message phrasing evolved over the study period (older *"NO INVESTIGATION NECESSARY"* vs. newer *"FIA STEWARDS: ... NO FURTHER ACTION"*).
- **Session context matters:** An ablation study shows telemetry-only features (no session-type flags) achieve F1-macro **0.687** vs. **0.887** with session context included — session type is a genuinely strong, legitimate signal, but it means part of the model's performance reflects enforcement context rather than pure driving physics.
- Labels reflect **FIA stewards' historical decisions**, which are themselves widely acknowledged to be inconsistent — the model approximates human judgment, not an independent ground truth.

---

## 📖 Citation

If you use this dataset or code, please cite:

```bibtex
@inproceedings{durrani2027trackimits,
  title     = {Beyond Detection: A Telemetry-Based Machine Learning Approach to Classifying Ambiguous Track Limit Violations in Formula 1},
  author    = {Durrani, Babar Khan},
  booktitle = {Proceedings of ICECT 2027},
  year      = {2027}
}
```

---

## 🙏 Acknowledgments

- Data sourced via [FastF1](https://github.com/theOehrly/Fast-F1) — an open-source Python library for accessing official Formula 1 timing and telemetry data.
- All data is publicly available and derived from F1's official live timing feeds. No proprietary FIA data was used.

---

## 📬 Contact

**Babar Khan Durrani**
BS Robotics and Intelligent Systems, Bahria University Islamabad
[GitHub](https://github.com/BabarKhanD)

---

<p align="center"><i>Built with 🏁 for a fairer, more transparent motorsport.</i></p>
