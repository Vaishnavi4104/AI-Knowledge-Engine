"""
Topic detection service using BERTopic for content gap analysis
"""

import logging
from typing import List, Dict, Optional
import pandas as pd
from bertopic import BERTopic
from bertopic.representation import KeyBERTInspired
import numpy as np

from app.services.embedding_service import embedding_service

logger = logging.getLogger(__name__)


class TopicService:
    """
    Service for topic detection and clustering using BERTopic
    """
    
    def __init__(self):
        """
        Initialize the topic detection service.
        """
        self.model: Optional[BERTopic] = None
        self.documents: List[str] = []
        self.topics_data: Optional[pd.DataFrame] = None
        self._initialize_model()
    
    def _initialize_model(self):
        """
        Initialize BERTopic model with custom configuration.
        """
        try:
            logger.info("Initializing BERTopic model...")
            
            # Use KeyBERT-inspired representation for better topic names
            representation_model = KeyBERTInspired()
            
            # Initialize BERTopic with custom settings
            # Use the same model name as embedding service
            embedding_model_name = embedding_service.model_name if embedding_service.model else "all-MiniLM-L6-v2"
            
            self.model = BERTopic(
                embedding_model=embedding_model_name,
                representation_model=representation_model,
                verbose=True,
                calculate_probabilities=True,
                min_topic_size=2,  # Minimum documents per topic
                nr_topics="auto",  # Automatically determine number of topics
            )
            
            logger.info("BERTopic model initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing BERTopic: {str(e)}")
            self.model = None
    
    def fit_topics(self, documents: List[str]) -> Dict:
        """
        Fit topics on a collection of documents.
        
        Args:
            documents (List[str]): List of document texts
            
        Returns:
            Dict: Topic modeling results
        """
        if not self.model:
            logger.error("BERTopic model not initialized")
            return {"error": "Model not initialized"}
        
        if not documents or len(documents) < 2:
            logger.warning("Not enough documents for topic modeling")
            return {
                "topics": [],
                "total_documents": len(documents) if documents else 0,
                "total_topics": 0
            }
        
        try:
            logger.info(f"Fitting topics on {len(documents)} documents...")
            
            # Store documents
            self.documents = documents
            
            # Fit the model
            topics, probs = self.model.fit_transform(documents)
            
            # Get topic information
            topic_info = self.model.get_topic_info()
            
            # Convert to list of dicts
            topics_list = []
            for _, row in topic_info.iterrows():
                if row['Topic'] == -1:  # Skip outlier topic
                    continue
                
                # Get representative docs for this topic
                topic_docs = [doc for doc, topic in zip(documents, topics) if topic == row['Topic']]
                
                topics_list.append({
                    'topic_id': int(row['Topic']),
                    'topic_name': str(row['Name']),
                    'count': int(row['Count']),
                    'representative_docs': topic_docs[:3],  # Top 3 docs
                    'percentage': round((row['Count'] / len(documents)) * 100, 2)
                })
            
            # Store topics data
            self.topics_data = topic_info
            
            result = {
                "topics": topics_list,
                "total_documents": len(documents),
                "total_topics": len(topics_list),
                "outlier_count": int(topic_info[topic_info['Topic'] == -1]['Count'].values[0]) if -1 in topic_info['Topic'].values else 0
            }
            
            logger.info(f"Identified {len(topics_list)} topics from {len(documents)} documents")
            return result
            
        except Exception as e:
            logger.error(f"Error fitting topics: {str(e)}")
            return {"error": str(e)}
    
    def get_topics(self, top_n: int = 10) -> List[Dict]:
        """
        Get top N topics from the fitted model.
        
        Args:
            top_n (int): Number of top topics to return
            
        Returns:
            List[Dict]: List of top topics
        """
        if not self.model or self.topics_data is None:
            return []
        
        try:
            # Filter out outlier topic (-1) and get top N
            valid_topics = self.topics_data[self.topics_data['Topic'] != -1]
            top_topics = valid_topics.nlargest(top_n, 'Count')
            
            topics_list = []
            for _, row in top_topics.iterrows():
                # Get words for this topic
                topic_words = self.model.get_topic(int(row['Topic']))
                words = [word[0] for word in topic_words[:5]]  # Top 5 words
                
                topics_list.append({
                    'topic_id': int(row['Topic']),
                    'topic_name': str(row['Name']),
                    'count': int(row['Count']),
                    'keywords': words,
                    'percentage': round((row['Count'] / len(self.documents)) * 100, 2) if self.documents else 0
                })
            
            return topics_list
            
        except Exception as e:
            logger.error(f"Error getting topics: {str(e)}")
            return []
    
    def predict_topic(self, text: str) -> Dict:
        """
        Predict the topic for a single document.
        
        Args:
            text (str): Document text
            
        Returns:
            Dict: Predicted topic information
        """
        if not self.model:
            return {"error": "Model not initialized"}
        
        if not self.topics_data is not None:
            return {"error": "Model not fitted. Call fit_topics first."}
        
        try:
            # Predict topic
            topic, prob = self.model.transform([text])
            
            topic_id = int(topic[0])
            confidence = float(prob[0][topic_id]) if prob is not None else 0.0
            
            # Get topic information
            if topic_id == -1:
                return {
                    'topic_id': -1,
                    'topic_name': 'Outlier',
                    'confidence': confidence,
                    'is_outlier': True
                }
            
            topic_info = self.topics_data[self.topics_data['Topic'] == topic_id]
            if not topic_info.empty:
                topic_name = str(topic_info.iloc[0]['Name'])
                topic_words = self.model.get_topic(topic_id)
                words = [word[0] for word in topic_words[:5]]
                
                return {
                    'topic_id': topic_id,
                    'topic_name': topic_name,
                    'confidence': confidence,
                    'keywords': words,
                    'is_outlier': False
                }
            else:
                return {
                    'topic_id': topic_id,
                    'topic_name': 'Unknown',
                    'confidence': confidence,
                    'is_outlier': False
                }
                
        except Exception as e:
            logger.error(f"Error predicting topic: {str(e)}")
            return {"error": str(e)}
    
    def detect_content_gaps(self, threshold: float = 0.1) -> List[Dict]:
        """
        Detect content gaps based on topic distribution.
        Topics with low representation indicate potential gaps.
        
        Args:
            threshold (float): Minimum percentage threshold for gap detection
            
        Returns:
            List[Dict]: List of detected content gaps
        """
        if not self.model or self.topics_data is None:
            return []
        
        try:
            gaps = []
            total_docs = len(self.documents)
            
            # Find topics with low representation
            valid_topics = self.topics_data[self.topics_data['Topic'] != -1]
            
            for _, row in valid_topics.iterrows():
                percentage = (row['Count'] / total_docs) * 100 if total_docs > 0 else 0
                
                if percentage < threshold * 100:
                    topic_words = self.model.get_topic(int(row['Topic']))
                    keywords = [word[0] for word in topic_words[:5]]
                    
                    gaps.append({
                        'topic_id': int(row['Topic']),
                        'topic_name': str(row['Name']),
                        'current_count': int(row['Count']),
                        'percentage': round(percentage, 2),
                        'keywords': keywords,
                        'gap_severity': 'high' if percentage < threshold * 50 else 'medium'
                    })
            
            # Sort by gap severity
            gaps.sort(key=lambda x: x['percentage'])
            
            return gaps
            
        except Exception as e:
            logger.error(f"Error detecting content gaps: {str(e)}")
            return []
    
    def get_model_info(self) -> Dict:
        """
        Get information about the topic model.
        
        Returns:
            Dict: Model information
        """
        return {
            'model_loaded': self.model is not None,
            'model_fitted': self.topics_data is not None,
            'total_documents': len(self.documents),
            'total_topics': len(self.topics_data) - 1 if self.topics_data is not None else 0  # Exclude outlier topic
        }


# Global topic service instance
topic_service = TopicService()

