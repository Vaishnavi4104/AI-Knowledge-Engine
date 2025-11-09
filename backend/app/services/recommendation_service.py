"""
Recommendation service using FAISS for vector similarity search
"""

import numpy as np
import faiss
from typing import List, Dict, Tuple, Optional
import logging
import pickle
import os
from pathlib import Path

from app.services.embedding_service import embedding_service

logger = logging.getLogger(__name__)


class RecommendationService:
    """
    Service for finding similar knowledge base articles using FAISS vector search
    """
    
    def __init__(self, index_path: Optional[str] = None):
        """
        Initialize the recommendation service.
        
        Args:
            index_path (str, optional): Path to save/load FAISS index
        """
        self.index: Optional[faiss.Index] = None
        self.knowledge_base: List[Dict] = []
        self.index_path = index_path or "data/faiss_index.bin"
        self.knowledge_base_path = "data/knowledge_base.pkl"
        self.dimension = 384  # Default for all-MiniLM-L6-v2
        self._load_or_build_index()
    
    def _load_or_build_index(self):
        """
        Load existing FAISS index or build a new one from knowledge base.
        """
        try:
            # Try to load existing index
            if os.path.exists(self.index_path) and os.path.exists(self.knowledge_base_path):
                logger.info(f"Loading FAISS index from {self.index_path}")
                self.index = faiss.read_index(self.index_path)
                
                with open(self.knowledge_base_path, 'rb') as f:
                    self.knowledge_base = pickle.load(f)
                
                self.dimension = self.index.d
                logger.info(f"Loaded index with {self.index.ntotal} vectors")
            else:
                logger.info("No existing index found. Building new index...")
                self._build_index_from_huggingface()
                
        except Exception as e:
            logger.error(f"Error loading index: {str(e)}")
            logger.info("Building new index...")
            self._build_index_from_huggingface()
    
    def _build_index_from_huggingface(self):
        """
        Build FAISS index from Hugging Face dataset.
        """
        try:
            from datasets import load_dataset
            
            logger.info("Loading dataset from Hugging Face: Tobi-Bueck/customer-support-tickets")
            dataset = load_dataset("Tobi-Bueck/customer-support-tickets", split="train")
            
            # Extract answers (knowledge base) and bodies (queries)
            answers = []
            bodies = []
            
            for item in dataset:
                if 'answer' in item and item['answer'] and item['answer'].strip():
                    answers.append({
                        'answer': item['answer'],
                        'body': item.get('body', ''),
                        'id': item.get('id', len(answers))
                    })
                if 'body' in item and item['body']:
                    bodies.append(item['body'])
            
            logger.info(f"Loaded {len(answers)} answers from dataset")
            
            if not answers:
                logger.warning("No answers found in dataset. Using mock data.")
                self._build_mock_index()
                return
            
            # Generate embeddings for all answers
            logger.info("Generating embeddings for knowledge base...")
            answer_texts = [item['answer'] for item in answers]
            embeddings, _ = embedding_service.generate_embeddings_batch(answer_texts)
            
            # Get dimension from embeddings
            self.dimension = len(embeddings[0]) if embeddings else 384
            
            # Convert to numpy array
            embeddings_array = np.array(embeddings).astype('float32')
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings_array)
            
            # Create FAISS index (L2 distance for normalized vectors = cosine distance)
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for normalized vectors
            self.index.add(embeddings_array)
            
            # Store knowledge base
            self.knowledge_base = answers
            
            # Save index and knowledge base
            self._save_index()
            
            logger.info(f"Built FAISS index with {self.index.ntotal} vectors")
            
        except Exception as e:
            logger.error(f"Error building index from Hugging Face: {str(e)}")
            logger.info("Falling back to mock index")
            self._build_mock_index()
    
    def _build_mock_index(self):
        """
        Build a mock FAISS index with sample knowledge base articles.
        """
        mock_articles = [
            {
                'id': 1,
                'answer': 'To reset your password, go to the login page and click "Forgot Password". Enter your email address and check your inbox for reset instructions.',
                'body': 'I forgot my password'
            },
            {
                'id': 2,
                'answer': 'Payment issues can be resolved by checking your payment method in account settings. Ensure your card is not expired and has sufficient funds.',
                'body': 'My payment failed'
            },
            {
                'id': 3,
                'answer': 'If you cannot log in, try clearing your browser cache and cookies. If the problem persists, contact support with your account email.',
                'body': 'Unable to login'
            },
            {
                'id': 4,
                'answer': 'To update your account information, navigate to Settings > Account and make the necessary changes. Changes take effect immediately.',
                'body': 'How do I update my account?'
            },
            {
                'id': 5,
                'answer': 'For subscription cancellation, go to Billing > Subscription and click Cancel. Your subscription will remain active until the end of the billing period.',
                'body': 'I want to cancel my subscription'
            }
        ]
        
        # Generate embeddings
        answer_texts = [item['answer'] for item in mock_articles]
        embeddings, _ = embedding_service.generate_embeddings_batch(answer_texts)
        
        self.dimension = len(embeddings[0]) if embeddings else 384
        embeddings_array = np.array(embeddings).astype('float32')
        
        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings_array)
        
        # Create index
        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(embeddings_array)
        
        self.knowledge_base = mock_articles
        self._save_index()
        
        logger.info(f"Built mock FAISS index with {self.index.ntotal} vectors")
    
    def _save_index(self):
        """
        Save FAISS index and knowledge base to disk.
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.index_path) if os.path.dirname(self.index_path) else ".", exist_ok=True)
            
            # Save index
            faiss.write_index(self.index, self.index_path)
            
            # Save knowledge base
            with open(self.knowledge_base_path, 'wb') as f:
                pickle.dump(self.knowledge_base, f)
            
            logger.info(f"Saved index and knowledge base to {self.index_path}")
            
        except Exception as e:
            logger.warning(f"Could not save index: {str(e)}")
    
    def recommend(self, query_text: str, top_k: int = 3) -> List[Dict]:
        """
        Find top-k similar articles for a given query.
        
        Args:
            query_text (str): Query text to find similar articles for
            top_k (int): Number of recommendations to return
            
        Returns:
            List[Dict]: List of recommended articles with similarity scores
        """
        if not self.index or self.index.ntotal == 0:
            logger.warning("Index is empty. Building index...")
            self._build_index_from_huggingface()
        
        if not query_text or not query_text.strip():
            return []
        
        try:
            # Generate embedding for query
            query_embedding, _ = embedding_service.generate_embedding(query_text)
            query_vector = np.array([query_embedding]).astype('float32')
            
            # Normalize for cosine similarity
            faiss.normalize_L2(query_vector)
            
            # Search in FAISS index
            distances, indices = self.index.search(query_vector, min(top_k, self.index.ntotal))
            
            # Get recommendations
            recommendations = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < 0 or idx >= len(self.knowledge_base):
                    continue
                
                article = self.knowledge_base[idx]
                recommendations.append({
                    'id': article.get('id', idx),
                    'answer': article.get('answer', ''),
                    'body': article.get('body', ''),
                    'similarity_score': float(distance),
                    'rank': i + 1
                })
            
            logger.info(f"Found {len(recommendations)} recommendations for query")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error in recommendation: {str(e)}")
            return []
    
    def add_article(self, answer_text: str, body_text: str = "") -> bool:
        """
        Add a new article to the knowledge base and index.
        
        Args:
            answer_text (str): Answer text for the knowledge base
            body_text (str): Original query/body text
            
        Returns:
            bool: True if successful
        """
        try:
            # Generate embedding
            embedding, _ = embedding_service.generate_embedding(answer_text)
            embedding_vector = np.array([embedding]).astype('float32')
            
            # Normalize
            faiss.normalize_L2(embedding_vector)
            
            # Add to index
            self.index.add(embedding_vector)
            
            # Add to knowledge base
            new_id = len(self.knowledge_base) + 1
            self.knowledge_base.append({
                'id': new_id,
                'answer': answer_text,
                'body': body_text
            })
            
            # Save updated index
            self._save_index()
            
            logger.info(f"Added new article to knowledge base (ID: {new_id})")
            return True
            
        except Exception as e:
            logger.error(f"Error adding article: {str(e)}")
            return False
    
    def get_index_stats(self) -> Dict:
        """
        Get statistics about the FAISS index.
        
        Returns:
            Dict: Index statistics
        """
        return {
            'total_vectors': self.index.ntotal if self.index else 0,
            'dimension': self.dimension,
            'index_type': type(self.index).__name__ if self.index else None,
            'knowledge_base_size': len(self.knowledge_base)
        }


# Global recommendation service instance
recommendation_service = RecommendationService()

