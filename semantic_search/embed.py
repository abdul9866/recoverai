import hashlib
import numpy as np
from pathlib import Path
from typing import List, Union

_text_model = None
_clip_model = None
_clip_preprocess = None
_torch = None

def _init_text_model():
    global _text_model
    if _text_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _text_model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception:
            _text_model = False

def _init_clip_model():
    global _clip_model, _clip_preprocess, _torch
    if _clip_model is None:
        try:
            import torch
            import open_clip
            _torch = torch
            model, _, preprocess = open_clip.create_model_and_transforms("ViT-B-32", pretrained="openai")
            _clip_model = model
            _clip_preprocess = preprocess
        except Exception:
            _clip_model = False

def _fallback_vector(input_str: str, dim: int = 384) -> List[float]:
    """Fallback normalized pseudo-embedding when Transformer models are offline."""
    hasher = hashlib.sha256(input_str.encode("utf-8")).digest()
    vec = np.zeros(dim, dtype=float)
    for i in range(dim):
        vec[i] = (hasher[i % len(hasher)] - 128) / 128.0
    norm = np.linalg.norm(vec)
    if norm > 1e-6:
        vec = vec / norm
    return vec.tolist()

def embed_text(text: str) -> List[float]:
    """Generates 384-dim normalized text vector embedding."""
    if not text.strip():
        return _fallback_vector("empty", dim=384)
    _init_text_model()
    if _text_model and hasattr(_text_model, "encode"):
        try:
            vec = _text_model.encode(text, normalize_embeddings=True)
            return vec.tolist()
        except Exception:
            pass
    return _fallback_vector(text, dim=384)

def embed_image(path: Union[str, Path]) -> List[float]:
    """Generates normalized CLIP vision embedding for image artifacts."""
    _init_clip_model()
    if _clip_model and _clip_preprocess and _torch:
        try:
            from PIL import Image
            img = _clip_preprocess(Image.open(path)).unsqueeze(0)
            with _torch.no_grad():
                feat = _clip_model.encode_image(img)
            feat = feat / feat.norm(dim=-1, keepdim=True)
            return feat.squeeze(0).tolist()
        except Exception:
            pass
    return _fallback_vector(str(path), dim=384)

def embed_query(query: str) -> List[float]:
    """Generates embedding for search query."""
    return embed_text(query)
