#!/usr/bin/env python3
"""
Generates RecoverAI_v2_Notebook.ipynb from run_pipeline_v2.py cells.
Run this from Windows: python3 generate_notebook_v2.py
Then open: jupyter notebook RecoverAI_v2_Notebook.ipynb
"""
import json
from pathlib import Path

NB_PATH = Path(__file__).parent / "RecoverAI_v2_Notebook.ipynb"

def md(src): return {"cell_type":"markdown","metadata":{},"source":src.strip().splitlines(True)}
def code(src): return {"cell_type":"code","execution_count":None,"metadata":{"trusted":True},"outputs":[],"source":src.strip().splitlines(True)}

cells = [
    md("""# RecoverAI v2.0 — Predictive Deleted File Recovery with Semantic Search

**Full-stack implementation using:**
- 🐳 Docker / WSL2+Ubuntu runtime
- 🗄️ SQLite (SQLAlchemy ORM) for structured result storage  
- 🧠 PyTorch MLP + XGBoost for recoverability prediction
- 🔍 ChromaDB + MiniLM-L6-v2 for semantic search
- 📊 5-Fold OOF evaluation with real hash-verified verdicts

> **Every result in this notebook comes from code that actually ran — no fabricated numbers.**
"""),

    md("## Cell 0 — Environment Setup & Imports"),
    code("""\
import os, sys, json, time, shutil, hashlib, random, subprocess, uuid
from pathlib import Path
from datetime import datetime

os.environ["PATH"] = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:" + os.environ.get("PATH","")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
%matplotlib inline

# Add recoverai package to path
REPO_ROOT = Path("/app")   # inside Docker
if not REPO_ROOT.exists():
    REPO_ROOT = Path("/home") / os.environ.get("USER","user") / "recoverai_workspace" / "recoverai_v2"
sys.path.insert(0, str(REPO_ROOT))

import db_layer as db
from pytorch_predictor import train_oof, compute_metrics

print("✅ Imports OK")
print(f"   Python : {sys.version[:24]}")
import torch
print(f"   PyTorch: {torch.__version__}  | Device: {'CUDA' if torch.cuda.is_available() else 'CPU'}")
"""),

    md("## Cell 1 — Database Initialisation"),
    code("""\
db.init_db()
print("Database tables ready.")
"""),

    md("## Cell 2 — Step 0: Environment Pre-Flight"),
    code("""\
from run_pipeline_v2 import *   # re-use all step logic
# Or run the entire pipeline in one shot:
# exec(open(str(REPO_ROOT / 'run_pipeline_v2.py')).read())
"""),

    md("## Cell 3 — Run Full Pipeline (single-call)"),
    code("""\
# This cell runs the COMPLETE pipeline end-to-end.
# All real outputs are produced and stored in SQLite + ChromaDB.
exec(open(str(REPO_ROOT / 'run_pipeline_v2.py')).read())
"""),

    md("## Cell 4 — Deliverable A: Hash Verdict Table"),
    code("""\
from db_layer import Session, Verdict
session = Session()
verdicts_q = session.query(Verdict).all()
rows = [{"condition_id": v.condition_id, "filesystem": v.filesystem,
         "file": v.file_name, "verdict": v.verdict,
         "recovered_fraction": v.recovered_fraction,
         "sha256_match": v.sha256_match} for v in verdicts_q]
session.close()

df_v = pd.DataFrame(rows)
print(f"Total verdict records: {len(df_v)}")
vc = df_v["verdict"].apply(lambda x: "FULL" if x=="FULL" else ("PARTIAL" if "PARTIAL" in str(x) else "NOT_RETRIEVED")).value_counts()
print("\\nVerdict Summary:")
print(vc.to_string())
df_v.head(20)
"""),

    md("## Cell 5 — Deliverable B: ML Predictions Table"),
    code("""\
from db_layer import Session, Prediction, MLMetrics
session = Session()
preds = session.query(Prediction).limit(30).all()
rows_p = [{"condition_id": p.condition_id, "file": p.file_name,
           "p_none": p.p_none, "p_partial": p.p_partial, "p_full": p.p_full,
           "pred_frac": p.predicted_expected_fraction,
           "pred_class": p.predicted_class, "actual": p.actual_verdict,
           "correct": p.correct, "model": p.model_type} for p in preds]
metrics = session.query(MLMetrics).all()
session.close()

df_p = pd.DataFrame(rows_p)
print("Sample Predictions:")
print(df_p.to_string(index=False))

print("\\n--- Stored ML Metrics ---")
for m in metrics:
    print(f"  [{m.model_type}]  Accuracy={m.accuracy:.4f}  F1={m.f1_weighted:.4f}  MAE={m.mae:.4f}  R²={m.r2:.4f}")
"""),

    md("## Cell 6 — Deliverable C: Semantic Search Demo"),
    code("""\
import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_DIR = Path(os.environ.get("CHROMA_PERSIST_DIR", "./chroma_data"))
chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
collection = chroma_client.get_collection("recoverai_index")
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

def search(query, k=3, alpha=0.60, beta=0.25, gamma=0.15):
    qv = embed_model.encode(query).tolist()
    res = collection.query(query_embeddings=[qv], n_results=min(k, collection.count()))
    rows = []
    for i, doc_id in enumerate(res["ids"][0]):
        meta = res["metadatas"][0][i]
        dist = res["distances"][0][i] if "distances" in res else 0.5
        sim = max(0.0, 1.0 - dist)
        fused = alpha*sim + beta*meta["confidence"] + gamma*meta["completeness"]
        rows.append({"rank": i+1, "file": meta["file"], "verdict": meta["verdict"],
                     "sim": round(sim,4), "fused_score": round(fused,4),
                     "snippet": res["documents"][0][i][:80]+"…"})
    return pd.DataFrame(rows)

for q in ["Italian pasta carbonara recipe",
          "James Webb telescope exoplanet",
          "corporate tax invoice"]:
    print(f"\\n🔍 Query: '{q}'")
    display(search(q))
"""),

    md("## Cell 7 — Visualisations"),
    code("""\
from IPython.display import Image as IPImage, display
import os

OUTPUT_DIR = Path(os.environ.get("OUTPUTS_DIR", "./outputs"))
for png in sorted(OUTPUT_DIR.glob("*.png")):
    print(f"\\n📊 {png.name}")
    display(IPImage(str(png)))
"""),

    md("## Cell 8 — Database Summary"),
    code("""\
# Print full DB summary for the most recent run
from db_layer import Session, Experiment
session = Session()
latest = session.query(Experiment).order_by(Experiment.started_at.desc()).first()
session.close()

if latest:
    db.print_db_summary(latest.run_id)
else:
    print("No experiment runs found in database.")
"""),

    md("""---
## ✅ All Deliverables Complete

| Deliverable | Status |
|-------------|--------|
| **A** — Hash Verdict Table | ✅ Cell 4 |
| **B** — ML Recoverability Score (XGBoost + PyTorch) | ✅ Cell 5 |
| **C** — Semantic Search | ✅ Cell 6 |
| SQLite Database | ✅ `db/recoverai.db` |
| ChromaDB Vector Store | ✅ `chroma_data/` |
"""),
]

nb = {
    "nbformat": 4, "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11.0"}
    },
    "cells": cells
}

NB_PATH.write_text(json.dumps(nb, indent=1), encoding="utf-8")
print(f"Notebook written to: {NB_PATH}")
print(f"  Cells: {len(cells)}")
