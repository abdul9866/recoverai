import os
from pathlib import Path
from typing import Dict, List, Optional

from common.config import CHROMA_DIR
from semantic_search.extract import extract_text, is_image
from semantic_search.embed import embed_text, embed_image, embed_query

_chroma_client = None
_collection = None

def get_chroma_collection():
    global _chroma_client, _collection
    if _collection is None:
        try:
            import chromadb
            CHROMA_DIR.mkdir(parents=True, exist_ok=True)
            _chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
            _collection = _chroma_client.get_or_create_collection("recovered_files")
        except Exception:
            _collection = False
    return _collection

# In-memory index fallback for fast unit testing / offline execution
_in_memory_index = []

def index_recovered_file(
    path: Path,
    recovery_confidence: float,
    completeness_fraction: float,
    file_id: Optional[str] = None
):
    """
    Indexes a recovered file artifact into the vector database along with its
    CARP recoverability confidence and completeness metadata.
    """
    path = Path(path)
    if not path.exists():
        return

    fid = file_id or str(path)

    if is_image(path):
        vec = embed_image(path)
    else:
        text = extract_text(path)
        if not text.strip():
            text = path.name  # Fallback to filename if text extraction is empty
        vec = embed_text(text)

    coll = get_chroma_collection()
    meta = {
        "path": str(path),
        "recovery_confidence": float(recovery_confidence),
        "completeness_fraction": float(completeness_fraction),
    }

    if coll:
        try:
            coll.add(
                ids=[fid],
                embeddings=[vec],
                metadatas=[meta]
            )
            return
        except Exception:
            pass

    # In-memory fallback index
    _in_memory_index.append({
        "id": fid,
        "path": str(path),
        "embedding": vec,
        "recovery_confidence": float(recovery_confidence),
        "completeness_fraction": float(completeness_fraction)
    })

def fused_search(
    query: str,
    k: int = 10,
    alpha: float = 0.6,
    beta: float = 0.25,
    gamma: float = 0.15
) -> List[Dict]:
    """
    CARP Component 3: Fused Semantic Vector Search.
    Ranks hits by vector similarity weighted with recovery confidence and byte completeness:
    FusedScore = alpha * Similarity + beta * Confidence + gamma * Completeness
    """
    qvec = embed_query(query)
    coll = get_chroma_collection()

    candidates = []
    if coll and hasattr(coll, "query"):
        try:
            raw = coll.query(query_embeddings=[qvec], n_results=max(k * 3, 20))
            if raw and raw.get("ids") and len(raw["ids"]) > 0:
                for i, doc_id in enumerate(raw["ids"][0]):
                    distance = raw["distances"][0][i] if "distances" in raw and raw["distances"] else 0.5
                    similarity = max(0.0, min(1.0, 1.0 - (distance / 2.0)))
                    meta = raw["metadatas"][0][i]
                    conf = meta.get("recovery_confidence", 1.0)
                    comp = meta.get("completeness_fraction", 1.0)
                    fused = (alpha * similarity) + (beta * conf) + (gamma * comp)
                    candidates.append({
                        "file_id": doc_id,
                        "path": meta.get("path", doc_id),
                        "similarity": round(similarity, 4),
                        "recovery_confidence": round(conf, 4),
                        "completeness_fraction": round(comp, 4),
                        "fused_score": round(fused, 4),
                    })
        except Exception:
            pass

    if not candidates and _in_memory_index:
        import numpy as np
        q_arr = np.array(qvec)
        for item in _in_memory_index:
            v_arr = np.array(item["embedding"])
            norm_q = np.linalg.norm(q_arr)
            norm_v = np.linalg.norm(v_arr)
            sim = float(np.dot(q_arr, v_arr) / (norm_q * norm_v)) if norm_q > 0 and norm_v > 0 else 0.0
            sim = max(0.0, min(1.0, (sim + 1.0) / 2.0))
            conf = item["recovery_confidence"]
            comp = item["completeness_fraction"]
            fused = (alpha * sim) + (beta * conf) + (gamma * comp)
            candidates.append({
                "file_id": item["id"],
                "path": item["path"],
                "similarity": round(sim, 4),
                "recovery_confidence": round(conf, 4),
                "completeness_fraction": round(comp, 4),
                "fused_score": round(fused, 4),
            })

    candidates.sort(key=lambda r: r["fused_score"], reverse=True)
    return candidates[:k]
