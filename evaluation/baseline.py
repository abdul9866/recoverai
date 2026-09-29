"""Naive baseline search and recovery strategy without CARP prioritization."""
from pathlib import Path
from typing import List

def baseline_search(query: str, recovered_dir: Path, k: int = 10) -> List[str]:
    """Plain filename and directory string matching search baseline."""
    query_terms = query.lower().split()
    hits = []
    recovered_path = Path(recovered_dir)
    if not recovered_path.exists():
        return []

    for path in recovered_path.rglob("*"):
        if path.is_file() and any(term in path.name.lower() for term in query_terms):
            hits.append(str(path))

    return hits[:k]
