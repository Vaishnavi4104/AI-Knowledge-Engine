"""
Text cleaning and preprocessing utilities
"""

import re
import string
from typing import List, Optional


class TextCleaner:
    """
    Utility class for cleaning and preprocessing text data
    """
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text input.
        
        Args:
            text (str): Raw text input
            
        Returns:
            str: Cleaned text
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation for context
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        
        # Remove multiple consecutive punctuation
        text = re.sub(r'([.!?]){2,}', r'\1', text)
        
        return text.strip()
    
    @staticmethod
    def extract_keywords(text: str, min_length: int = 3) -> List[str]:
        """
        Extract keywords from text.
        
        Args:
            text (str): Input text
            min_length (int): Minimum keyword length
            
        Returns:
            List[str]: List of extracted keywords
        """
        if not text:
            return []
        
        # Clean the text first
        cleaned_text = TextCleaner.clean_text(text)
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
        }
        
        # Split into words and filter
        words = cleaned_text.split()
        keywords = [
            word for word in words 
            if len(word) >= min_length and word not in stop_words
        ]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for word in keywords:
            if word not in seen:
                seen.add(word)
                unique_keywords.append(word)
        
        return unique_keywords
    
    @staticmethod
    def detect_priority_keywords(text: str) -> dict:
        """
        Detect priority-related keywords in text.
        
        Args:
            text (str): Input text
            
        Returns:
            dict: Dictionary with detected keywords by priority level
        """
        if not text:
            return {"high": [], "medium": [], "low": []}
        
        text_lower = text.lower()
        
        # Define priority keywords
        high_priority_keywords = [
            'error', 'failed', 'urgent', 'critical', 'not working', 'crash', 
            'down', 'issue immediately', 'broken', 'emergency', 'asap'
        ]
        
        medium_priority_keywords = [
            'delay', 'problem', 'help', 'trouble', 'stuck', 'confusion', 
            'question', 'issue', 'bug', 'slow', 'difficulty'
        ]
        
        low_priority_keywords = [
            'question', 'inquiry', 'information', 'request', 'suggestion',
            'feedback', 'improvement', 'feature'
        ]
        
        # Find matches
        detected = {
            "high": [],
            "medium": [],
            "low": []
        }
        
        for keyword in high_priority_keywords:
            if keyword in text_lower:
                detected["high"].append(keyword)
        
        for keyword in medium_priority_keywords:
            if keyword in text_lower:
                detected["medium"].append(keyword)
        
        for keyword in low_priority_keywords:
            if keyword in text_lower:
                detected["low"].append(keyword)
        
        return detected
    
    @staticmethod
    def extract_sentiment_indicators(text: str) -> dict:
        """
        Extract sentiment indicators from text.
        
        Args:
            text (str): Input text
            
        Returns:
            dict: Sentiment analysis results
        """
        if not text:
            return {"sentiment": "neutral", "confidence": 0.5, "indicators": []}
        
        text_lower = text.lower()
        
        # Positive indicators
        positive_words = [
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'perfect',
            'love', 'like', 'satisfied', 'happy', 'pleased', 'thank'
        ]
        
        # Negative indicators
        negative_words = [
            'bad', 'terrible', 'awful', 'hate', 'angry', 'frustrated',
            'disappointed', 'annoyed', 'upset', 'wrong', 'broken', 'failed'
        ]
        
        # Count occurrences
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        # Determine sentiment
        if positive_count > negative_count:
            sentiment = "positive"
            confidence = min(0.9, 0.5 + (positive_count * 0.1))
        elif negative_count > positive_count:
            sentiment = "negative"
            confidence = min(0.9, 0.5 + (negative_count * 0.1))
        else:
            sentiment = "neutral"
            confidence = 0.5
        
        # Collect all indicators
        indicators = []
        indicators.extend([word for word in positive_words if word in text_lower])
        indicators.extend([word for word in negative_words if word in text_lower])
        
        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "indicators": indicators
        }
    
    @staticmethod
    def preprocess_for_embedding(text: str) -> str:
        """
        Preprocess text specifically for embedding generation.
        
        Args:
            text (str): Input text
            
        Returns:
            str: Preprocessed text ready for embedding
        """
        if not text:
            return ""
        
        # Basic cleaning
        text = TextCleaner.clean_text(text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
        
        # Remove phone numbers
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '', text)
        
        # Remove excessive punctuation
        text = re.sub(r'[.]{2,}', '.', text)
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        
        # Final cleanup
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
