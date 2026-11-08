# RecoverAI System Architecture

RecoverAI is an intelligent, three-stage digital forensics framework engineered for predictive deleted file recovery, triage knapsack prioritization, and semantic evidence retrieval across modern flash-friendly filesystems (F2FS).

---

## 1. Modular High-Level Architecture

`
[ Raw Disk Image / Bitstream (.dd, .raw, .E01) ]
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  STAGE 1: Recoverability Predictor (predictor/)             │
│  - 18 Forensic Feature Extraction                           │
│  - Deep MLP (RecoverabilityNet) + XGBoost Soft-Voting       │
│  - Class-Balanced Focal Loss Calibration                    │
│  - Output: Integrity Confidence Score P_i ∈ [0, 1]          │
└──────────────────────────────┬──────────────────────────────┘
                               │ P_i & Estimated Extraction Cost T_i
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  STAGE 2: F2FS Recovery Engine & CARP (recovery_engine/)    │
│  - 0/1 Greedy Knapsack Prioritization (max ∑ P_i · V_i)     │
│  - Unallocated Segment Scanning (SIT / SSA filter)          │
│  - 4KB Node-Block Carving & Virtual NAT Generation          │
│  - Log Sequence Timestamp Deduplication                     │
│  - Recursive Dentry Path & Filename Restoration             │
│  - Graceful /lost+found Fallback for Severed Paths          │
└──────────────────────────────┬──────────────────────────────┘
                               │ Carved Verified File Payloads
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  STAGE 3: Forensic Semantic Search (semantic_search/)       │
│  - Automated Text Parsing & Local Tesseract OCR             │
│  - 384-dimensional Dense Embeddings (all-MiniLM-L6-v2)       │
│  - ChromaDB Local Vector Store with HNSW Indexing           │
│  - Cosine Similarity & CARP Fused Evidence Ranking          │
│  - Air-Gapped, On-Device Legal Privacy (ISO/IEC 27037)      │
└─────────────────────────────────────────────────────────────┘
`

---

## 2. Directory & Module Responsibilities

### predictor/ (Stage 1)
* **eatures.py**: Extracts the 18-dimensional forensic feature vector spanning structural integrity, spatial continuity, temporal/GC exposure, and Shannon entropy.
* **model.py**: Implements the ensemble classifier combining RecoverabilityNet (PyTorch 4-layer Deep MLP) with XGBoost.
* **	rain.py**: Model training routine applying Class-Balanced Focal Loss ($\gamma = 2.0, lpha = 0.25$) to handle severe class imbalance between dead flash blocks and intact files.
* **predict.py**: High-performance inference endpoint outputting calibrated confidence scores across High ($\ge 0.75$), Medium (.40–0.74$), and Low ($< 0.40$) recoverability bands.
* **dataset/**: Ground-truth dataset generators (generate_deletions.py, conditions.py) and training data corpus (data/recoverability_dataset.csv).

### 
ecovery_engine/ (Stage 2)
* **orchestrator.py**: CARP Knapsack optimization scheduler and workflow conductor. Manages carving jobs within examiner-specified time budgets $.
* **2fs_extension.py**: F2FS-specific carving kernel implementing unallocated segment parsing, Virtual NAT synthesis, and directory dentry tree reconstruction.
* **strategies.py**: Recovery prioritization strategies comparing CARP greedy knapsack against sequential, size-first, and random carving baselines.

### semantic_search/ (Stage 3)
* **embed.py**: Local, air-gapped dense vector embedding generation using sentence-transformers/all-MiniLM-L6-v2 (384 dimensions).
* **extract.py**: Multi-format textual content extraction supporting PDF, DOCX, TXT, SQLite, and image OCR via Tesseract.
* **index.py**: Persistent ChromaDB HNSW collection management, indexing recovered files with metadata and confidence scores.
* **search_cli.py**: Natural-language query interface for investigators (e.g., *'Find documents related to financial wire transfers'*).

### common/
* **config.py**: Global filesystem paths, model hyperparameters, and execution thresholds.
* **schema.py**: Pydantic data schemas defining DeletedFileRecord, Filesystem, Medium, and RecoveryVerdict.

### evaluation/
* **metrics.py**: Standardized forensic evaluation metrics (False Recovery Rate, Precision@k, Recall, Macro AUC-ROC, Cryptographic SHA-256 Hash Ground Truth).
* **aseline.py**: Conventional carving baseline models for comparative benchmarks.
* **dashboard.py**: Triage performance and metric reporting utilities.

### 	ests/
* Automated test suite covering unit, orchestrator, predictor, and end-to-end integration workflows.
