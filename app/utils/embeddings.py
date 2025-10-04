from __future__ import annotations

from functools import lru_cache
from typing import List

from app.utils.settings import settings


@lru_cache(maxsize=1)
def _model():
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "Semantic search is enabled but 'sentence-transformers' is not installed.\n"
            "Install with: pip install sentence-transformers"
        ) from e
    return SentenceTransformer(settings.embedding_model)


def embed_text(text: str) -> List[float]:
    vec = _model().encode(text or "", normalize_embeddings=True)
    try:
        import numpy as np  # type: ignore
        if isinstance(vec, np.ndarray):
            return vec.astype(float).tolist()
    except Exception:
        pass
    return [float(x) for x in vec]
