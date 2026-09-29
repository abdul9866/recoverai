from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
XCARVER_PATH = BASE_DIR / "vendor" / "xcarver"
DATASET_DIR = BASE_DIR / "predictor" / "dataset" / "data"
MODEL_PATH = BASE_DIR / "predictor" / "model.joblib"
CHROMA_DIR = BASE_DIR / "semantic_search" / "chroma_db"
DEFAULT_BUDGET_SECONDS = 3600     # investigator time budget, override via CLI
