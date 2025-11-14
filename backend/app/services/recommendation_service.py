"""
Recommendation service using FAISS for vector similarity search
"""

import logging
import os
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import faiss
import numpy as np

from app.core.config import get_settings
from app.services.embedding_service import embedding_service

logger = logging.getLogger(__name__)
settings = get_settings()


class RecommendationService:
    """Service for finding similar knowledge base articles using FAISS."""

    def __init__(self, index_path: Optional[str] = None, kb_path: Optional[str] = None):
        self.index: Optional[faiss.Index] = None
        self.knowledge_base: List[Dict] = []
        self.index_path = Path(index_path or settings.faiss_index_path)
        self.knowledge_base_path = Path(
            kb_path or settings.knowledge_base_path
        )
        self.dimension = 384  # Default for all-MiniLM-L6-v2
        self._load_or_build_index()

    def _load_or_build_index(self):
        """Load existing FAISS index or build a new one from knowledge base."""

        try:
            index_exists = self.index_path.exists()
            kb_exists = self.knowledge_base_path.exists()

            if index_exists and kb_exists:
                logger.info("Loading FAISS index from %s", self.index_path)
                self.index = faiss.read_index(str(self.index_path))

                with self.knowledge_base_path.open("rb") as file:
                    self.knowledge_base = pickle.load(file)

                self.dimension = self.index.d
                logger.info(
                    "Loaded FAISS index with %s vectors", self.index.ntotal
                )
            else:
                if not index_exists:
                    logger.info(
                        "FAISS index not found at %s. Building new index...",
                        self.index_path,
                    )
                if not kb_exists:
                    logger.info(
                        "Knowledge base not found at %s. Attempting rebuild...",
                        self.knowledge_base_path,
                    )
                self._build_index_from_huggingface()

        except Exception as exc:  # pragma: no cover - runtime protection
            logger.exception("Error loading FAISS index: %s", exc)
            logger.info("Rebuilding index from source data.")
            self._build_index_from_huggingface()

    def _build_index_from_huggingface(self):
        """Build FAISS index from Hugging Face dataset."""

        try:
            from datasets import load_dataset

            logger.info(
                "Loading dataset from Hugging Face: Tobi-Bueck/customer-support-tickets"
            )
            # Use token if available (for gated datasets)
            token = settings.huggingface_token if settings.huggingface_token else None
            dataset = load_dataset(
                "Tobi-Bueck/customer-support-tickets", 
                split="train",
                token=token
            )

            answers: List[Dict] = []

            for item in dataset:
                if item.get("answer") and item["answer"].strip():
                    answers.append(
                        {
                            "answer": item["answer"],
                            "body": item.get("body", ""),
                            "id": item.get("id", len(answers)),
                        }
                    )

            logger.info("Loaded %s answers from dataset", len(answers))

            if not answers:
                logger.warning("No answers found in dataset. Using mock data.")
                self._build_mock_index()
                return

            logger.info("Generating embeddings for knowledge base...")
            answer_texts = [item["answer"] for item in answers]
            embeddings, _ = embedding_service.generate_embeddings_batch(answer_texts)

            self.dimension = len(embeddings[0]) if embeddings else 384
            embeddings_array = np.array(embeddings).astype("float32")
            faiss.normalize_L2(embeddings_array)

            self.index = faiss.IndexFlatIP(self.dimension)
            self.index.add(embeddings_array)

            self.knowledge_base = answers
            self._save_index()

            logger.info("Built FAISS index with %s vectors", self.index.ntotal)

        except Exception as exc:  # pragma: no cover - runtime protection
            logger.exception("Error building index from dataset: %s", exc)
            logger.info("Falling back to mock index")
            self._build_mock_index()

    def _build_mock_index(self):
        """Build a mock FAISS index with sample knowledge base articles."""

        mock_articles = [
            {
                "id": 1,
                "answer": 'To reset your password, go to the login page and click "Forgot Password". Enter your email address and check your inbox for reset instructions.',
                "body": "I forgot my password",
            },
            {
                "id": 2,
                "answer": "Payment issues can be resolved by checking your payment method in account settings. Ensure your card is not expired and has sufficient funds.",
                "body": "My payment failed",
            },
            {
                "id": 3,
                "answer": "If you cannot log in, try clearing your browser cache and cookies. If the problem persists, contact support with your account email.",
                "body": "Unable to login",
            },
            {
                "id": 4,
                "answer": "To update your account information, navigate to Settings > Account and make the necessary changes. Changes take effect immediately.",
                "body": "How do I update my account?",
            },
            {
                "id": 5,
                "answer": "For subscription cancellation, go to Billing > Subscription and click Cancel. Your subscription will remain active until the end of the billing period.",
                "body": "I want to cancel my subscription",
            },
        ]

        answer_texts = [item["answer"] for item in mock_articles]
        embeddings, _ = embedding_service.generate_embeddings_batch(answer_texts)

        self.dimension = len(embeddings[0]) if embeddings else 384
        embeddings_array = np.array(embeddings).astype("float32")
        faiss.normalize_L2(embeddings_array)

        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(embeddings_array)

        self.knowledge_base = mock_articles
        self._save_index()

        logger.info("Built mock FAISS index with %s vectors", self.index.ntotal)

    def _save_index(self):
        """Persist FAISS index and knowledge base to disk."""

        try:
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            self.knowledge_base_path.parent.mkdir(parents=True, exist_ok=True)

            faiss.write_index(self.index, str(self.index_path))

            with self.knowledge_base_path.open("wb") as file:
                pickle.dump(self.knowledge_base, file)

            logger.info(
                "Saved FAISS index to %s and knowledge base to %s",
                self.index_path,
                self.knowledge_base_path,
            )

        except Exception as exc:  # pragma: no cover - filesystem errors
            logger.warning("Could not save FAISS index: %s", exc)

    def recommend(self, query_text: str, top_k: int = 3) -> List[Dict]:
        """Find top-k similar articles for a given query."""

        if not self.index or self.index.ntotal == 0:
            logger.warning("Index is empty. Building index...")
            self._build_index_from_huggingface()

        if not query_text or not query_text.strip():
            return []

        try:
            query_embedding, _ = embedding_service.generate_embedding(query_text)
            query_vector = np.array([query_embedding]).astype("float32")
            faiss.normalize_L2(query_vector)

            distances, indices = self.index.search(
                query_vector, min(top_k, self.index.ntotal)
            )

            recommendations = []
            for rank, (distance, idx) in enumerate(zip(distances[0], indices[0]), start=1):
                if idx < 0 or idx >= len(self.knowledge_base):
                    continue

                article = self.knowledge_base[idx]
                recommendations.append(
                    {
                        "id": article.get("id", idx),
                        "answer": article.get("answer", ""),
                        "body": article.get("body", ""),
                        "similarity_score": float(distance),
                        "rank": rank,
                    }
                )

            logger.info("Found %s recommendations for query", len(recommendations))
            return recommendations

        except Exception as exc:  # pragma: no cover - runtime protection
            logger.exception("Error generating recommendations: %s", exc)
            return []

    def add_article(self, answer_text: str, body_text: str = "") -> bool:
        """Add a new article to the knowledge base and index."""

        try:
            embedding, _ = embedding_service.generate_embedding(answer_text)
            embedding_vector = np.array([embedding]).astype("float32")
            faiss.normalize_L2(embedding_vector)

            if self.index is None:
                self.dimension = embedding_vector.shape[1]
                self.index = faiss.IndexFlatIP(self.dimension)

            self.index.add(embedding_vector)

            new_id = len(self.knowledge_base) + 1
            self.knowledge_base.append(
                {"id": new_id, "answer": answer_text, "body": body_text}
            )

            self._save_index()
            logger.info("Added new article to knowledge base (ID: %s)", new_id)
            return True

        except Exception as exc:  # pragma: no cover - runtime protection
            logger.exception("Error adding article to knowledge base: %s", exc)
            return False

    def get_index_stats(self) -> Dict:
        """Return statistics about the FAISS index."""

        return {
            "total_vectors": self.index.ntotal if self.index else 0,
            "dimension": self.dimension,
            "index_type": type(self.index).__name__ if self.index else None,
            "knowledge_base_size": len(self.knowledge_base),
            "index_path": str(self.index_path),
        }


# Global recommendation service instance
recommendation_service = RecommendationService()

