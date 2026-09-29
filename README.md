# RecoverAI v2.0
## Predictive Deleted File Recovery with Semantic Search

> A capstone research project implementing forensic file-carving, ML-based recoverability prediction, and semantic search over recovered artifacts.

---

## Tech Stack (Component Table)

| Component | Use |
|-----------|-----|
| **Antigravity 2.0** | AI coding / development environment |
| **Python 3.11** | Entire RecoverAI implementation |
| **WSL2 + Ubuntu** | Linux environment for filesystem/forensic work |
| **Docker** | Isolated services and reproducible environment |
| **Git + GitHub** | Version control |
| **SQLite / PostgreSQL** | Metadata & results storage (`recoverai.db`) |
| **ChromaDB** | Vector database for semantic search |
| **scikit-learn / PyTorch** | Recoverability predictor (XGBoost baseline + PyTorch MLP) |
| **F2FS tools / custom Python** | Recovery Engine |

---

## Quick Start

### Option A — Docker (Recommended, fully reproducible)

```bash
# Build + run the pipeline once
docker-compose up --build recoverai

# Or open Jupyter Lab interactively at http://localhost:8888
# Token: recoverai2026
docker-compose up --build jupyter
```

### Option B — WSL2 / Ubuntu (Direct)

```bash
# 1. Install system forensic tools
sudo apt-get install -y e2fsprogs dosfstools f2fs-tools ntfs-3g util-linux poppler-utils

# 2. Clone xCarver
mkdir -p ~/recoverai_workspace && cd ~/recoverai_workspace
git clone https://github.com/z0rhack/xcarver

# 3. Install Python dependencies
pip3 install -r requirements.txt

# 4. Run as root (mount requires root)
sudo python3 run_pipeline_v2.py
```

---

## Project Structure

```
recoverai/
├── run_pipeline_v2.py        ← Main pipeline (v2: SQLite + PyTorch + Docker-aware)
├── db_layer.py               ← SQLAlchemy ORM (SQLite / PostgreSQL)
├── pytorch_predictor.py      ← PyTorch MLP multi-task classifier + regressor
├── RecoverAI_v2_Notebook.ipynb  ← Interactive Jupyter notebook
├── Dockerfile                ← Ubuntu 22.04 container with all forensic tools
├── docker-compose.yml        ← Services: pipeline, jupyter, postgres (optional)
├── requirements.txt          ← Pinned Python dependencies
├── outputs/                  ← CSV exports, PNG plots (git-ignored)
├── db/                       ← recoverai.db SQLite database (git-ignored)
└── chroma_data/              ← ChromaDB vector store (git-ignored)
```

---

## Deliverables

| ID | Deliverable | Description |
|----|-------------|-------------|
| **A** | **Hash Verdicts Table** | Per-file SHA-256 comparison — `FULL`, `PARTIAL_XX%`, `NOT_RETRIEVED` |
| **B** | **Recoverability Score** | PyTorch MLP 5-fold OOF: `p_none`, `p_partial`, `p_full`, `predicted_fraction` |
| **C** | **Semantic Search** | ChromaDB + MiniLM-L6-v2, fused score `0.60·Sim + 0.25·Conf + 0.15·Completeness` |

---

## ML Models

### XGBoost (Baseline)
- 5-fold OOF cross-validation
- Features: filesystem_code, discard, occupancy, filler_MB, file_type, size, elapsed_s

### PyTorch MLP (Main Model)
```
Input(7) → Linear(64) → BN → ReLU → Dropout(0.30)
         → Linear(32) → BN → ReLU → Dropout(0.20)
         → [CLF] Linear(32→3)  ← CrossEntropyLoss
         → [REG] Linear(32→1) → Sigmoid  ← MSELoss
```
- Multi-task: simultaneous classification + regression heads
- Early stopping (patience=10) + ReduceLROnPlateau scheduler
- Adam optimizer, weight_decay=1e-4

---

## Database Schema

All results are stored in **SQLite** (`db/recoverai.db`) via SQLAlchemy ORM:

| Table | Contents |
|-------|---------|
| `experiments` | Run metadata, git commit, timestamps |
| `manifest` | Pre-deletion file SHA-256 and block hashes |
| `verdicts` | Per-file recovery verdict per condition |
| `predictions` | ML model predictions aligned with verdicts |
| `allocations` | Knapsack effort allocations |
| `search_index` | Vector search metadata |
| `ml_metrics` | Accuracy, F1, MAE, R², FRR per model |

Query example:
```python
from db_layer import Session, Verdict
session = Session()
rows = session.query(Verdict).filter_by(verdict="FULL").all()
```

---

## Authors
RecoverAI Research Team — Capstone Project 2026
