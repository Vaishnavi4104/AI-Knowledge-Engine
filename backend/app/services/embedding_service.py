"""
Embedding service using SentenceTransformer for text vectorization
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional, Tuple
import logging
import time
from functools import lru_cache

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating text embeddings using SentenceTransformer
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding service.
        
        Args:
            model_name (str): Name of the SentenceTransformer model to use
        """
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """
        Load the SentenceTransformer model.
        Uses caching to avoid reloading the model.
        """
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            start_time = time.time()
            
            self.model = SentenceTransformer(self.model_name)
            
            load_time = time.time() - start_time
            logger.info(f"Model loaded successfully in {load_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Failed to load embedding model: {str(e)}")
            raise RuntimeError(f"Could not load embedding model: {str(e)}")
    
    def generate_embedding(self, text: str) -> Tuple[List[float], Dict]:
        """
        Generate embedding for a single text.
        
        Args:
            text (str): Input text to embed
            
        Returns:
            Tuple[List[float], Dict]: Embedding vector and metadata
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        try:
            start_time = time.time()
            
            # Generate embedding
            embedding = self.model.encode(text, convert_to_tensor=False)
            
            # Convert to list
            embedding_list = embedding.tolist()
            
            processing_time = time.time() - start_time
            
            metadata = {
                "model_name": self.model_name,
                "embedding_dimension": len(embedding_list),
                "processing_time_ms": round(processing_time * 1000, 2),
                "text_length": len(text),
                "text_preview": text[:100] + "..." if len(text) > 100 else text
            }
            
            logger.debug(f"Generated embedding in {processing_time:.3f}s for text length {len(text)}")
            
            return embedding_list, metadata
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise RuntimeError(f"Failed to generate embedding: {str(e)}")
    
    def generate_embeddings_batch(self, texts: List[str]) -> Tuple[List[List[float]], Dict]:
        """
        Generate embeddings for multiple texts in batch.
        
        Args:
            texts (List[str]): List of input texts
            
        Returns:
            Tuple[List[List[float]], Dict]: List of embedding vectors and metadata
        """
        if not texts:
            raise ValueError("Texts list cannot be empty")
        
        try:
            start_time = time.time()
            
            # Generate embeddings in batch
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            
            # Convert to list of lists
            embeddings_list = [emb.tolist() for emb in embeddings]
            
            processing_time = time.time() - start_time
            
            metadata = {
                "model_name": self.model_name,
                "batch_size": len(texts),
                "embedding_dimension": len(embeddings_list[0]) if embeddings_list else 0,
                "processing_time_ms": round(processing_time * 1000, 2),
                "avg_processing_time_ms": round((processing_time * 1000) / len(texts), 2) if texts else 0
            }
            
            logger.info(f"Generated {len(texts)} embeddings in {processing_time:.3f}s")
            
            return embeddings_list, metadata
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            raise RuntimeError(f"Failed to generate batch embeddings: {str(e)}")
    
    def get_embedding_preview(self, embedding: List[float], preview_size: int = 5) -> List[float]:
        """
        Get a preview of the first few values of an embedding.
        
        Args:
            embedding (List[float]): Full embedding vector
            preview_size (int): Number of values to include in preview
            
        Returns:
            List[float]: First few values of the embedding
        """
        return embedding[:preview_size]
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1 (List[float]): First embedding vector
            embedding2 (List[float]): Second embedding vector
            
        Returns:
            float: Cosine similarity score (-1 to 1)
        """
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def get_model_info(self) -> Dict:
        """
        Get information about the loaded model.
        
        Returns:
            Dict: Model information
        """
        return {
            "model_name": self.model_name,
            "model_loaded": self.model is not None,
            "max_seq_length": getattr(self.model, 'max_seq_length', 'Unknown'),
            "embedding_dimension": self.model.get_sentence_embedding_dimension() if self.model else None
        }


# Global embedding service instance
embedding_service = EmbeddingService()
