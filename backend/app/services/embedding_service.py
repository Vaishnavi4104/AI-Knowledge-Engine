"""
Embedding service using SentenceTransformer for text vectorization
"""

import logging
import time
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class EmbeddingService:
    """Service for generating text embeddings using SentenceTransformer."""

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.embedding_model_name
        self.model: Optional[SentenceTransformer] = None
        self._load_model()

    def _load_model(self):
        """Load the SentenceTransformer model if not already loaded."""

        if self.model is not None:
            return

        try:
            logger.info("Loading embedding model: %s", self.model_name)
            start_time = time.time()

            self.model = SentenceTransformer(self.model_name)

            load_time = time.time() - start_time
            logger.info("Model loaded successfully in %.2f seconds", load_time)

        except Exception as exc:  # pragma: no cover - runtime protection
            logger.exception("Failed to load embedding model: %s", exc)
            raise RuntimeError(f"Could not load embedding model: {exc}") from exc

    def generate_embedding(self, text: str) -> Tuple[List[float], Dict]:
        """Generate embedding for a single text."""

        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        if self.model is None:
            self._load_model()

        try:
            start_time = time.time()

            embedding = self.model.encode(text, convert_to_tensor=False)
            embedding_list = embedding.tolist()

            processing_time = time.time() - start_time

            metadata = {
                "model_name": self.model_name,
                "embedding_dimension": len(embedding_list),
                "processing_time_ms": round(processing_time * 1000, 2),
                "text_length": len(text),
                "text_preview": text[:100] + "..." if len(text) > 100 else text,
            }

            logger.debug(
                "Generated embedding in %.3fs for text length %s",
                processing_time,
                len(text),
            )

            return embedding_list, metadata

        except Exception as exc:  # pragma: no cover - runtime protection
            logger.exception("Error generating embedding: %s", exc)
            raise RuntimeError(f"Failed to generate embedding: {exc}") from exc

    def generate_embeddings_batch(self, texts: List[str]) -> Tuple[List[List[float]], Dict]:
        """Generate embeddings for multiple texts in batch."""

        if not texts:
            raise ValueError("Texts list cannot be empty")

        if self.model is None:
            self._load_model()

        try:
            start_time = time.time()

            embeddings = self.model.encode(texts, convert_to_tensor=False)
            embeddings_list = [emb.tolist() for emb in embeddings]

            processing_time = time.time() - start_time

            metadata = {
                "model_name": self.model_name,
                "batch_size": len(texts),
                "embedding_dimension": len(embeddings_list[0]) if embeddings_list else 0,
                "processing_time_ms": round(processing_time * 1000, 2),
                "avg_processing_time_ms": round((processing_time * 1000) / len(texts), 2)
                if texts
                else 0,
            }

            logger.info(
                "Generated %s embeddings in %.3fs", len(texts), processing_time
            )

            return embeddings_list, metadata

        except Exception as exc:  # pragma: no cover - runtime protection
            logger.exception("Error generating batch embeddings: %s", exc)
            raise RuntimeError(f"Failed to generate batch embeddings: {exc}") from exc

    def get_embedding_preview(self, embedding: List[float], preview_size: int = 5) -> List[float]:
        """Return the first few values of an embedding for preview purposes."""

        return embedding[:preview_size]

    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings."""

        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)

            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            similarity = dot_product / (norm1 * norm2)
            return float(similarity)

        except Exception as exc:  # pragma: no cover - runtime protection
            logger.exception("Error calculating similarity: %s", exc)
            return 0.0

    def get_model_info(self) -> Dict:
        """Return information about the loaded model."""

        return {
            "model_name": self.model_name,
            "model_loaded": self.model is not None,
            "max_seq_length": getattr(self.model, "max_seq_length", "Unknown")
            if self.model
            else None,
            "embedding_dimension": self.model.get_sentence_embedding_dimension()
            if self.model
            else None,
        }


# Global embedding service instance
embedding_service = EmbeddingService()
