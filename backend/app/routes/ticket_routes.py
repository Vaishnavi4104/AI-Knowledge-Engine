"""
Ticket analysis API routes
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
import logging
import time
from datetime import datetime

from app.db.database import get_db, create_tables
from app.db.schemas import TicketAnalysis
from app.services.embedding_service import embedding_service
from app.services.language_service import language_service
from app.services.recommendation_service import recommendation_service
from app.services.topic_service import topic_service
from app.utils.text_cleaner import TextCleaner
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class TicketAnalysisRequest(BaseModel):
    """
    Request model for ticket analysis
    """
    text: str
    file_name: Optional[str] = None


class TicketAnalysisResponse(BaseModel):
    """
    Response model for ticket analysis
    """
    priority: str
    category: str
    sentiment: str
    language: dict
    confidence: float
    embedding_preview: list
    detected_keywords: list
    suggested_articles: list
    processing_time_ms: float
    model_info: dict


class RecommendRequest(BaseModel):
    """
    Request model for article recommendation
    """
    text: str


class RecommendResponse(BaseModel):
    """
    Response model for recommendations
    """
    recommendations: list
    query_text: str
    total_results: int


class TopicsResponse(BaseModel):
    """
    Response model for topics
    """
    topics: list
    total_topics: int
    total_documents: int
    content_gaps: list


class UsageResponse(BaseModel):
    """
    Response model for usage statistics
    """
    most_used: list
    least_used: list
    total_articles: int
    usage_stats: dict


class PriorityAnalyzer:
    """
    Priority analysis logic
    """
    
    @staticmethod
    def analyze_priority(text: str) -> dict:
        """
        Analyze ticket priority based on keyword matching.
        
        Args:
            text (str): Ticket text content
            
        Returns:
            dict: Priority analysis results
        """
        text_lower = text.lower()
        
        # High priority keywords
        high_priority_keywords = [
            'error', 'failed', 'urgent', 'critical', 'not working', 
            'crash', 'down', 'issue immediately', 'broken', 'emergency', 'asap'
        ]
        
        # Medium priority keywords
        medium_priority_keywords = [
            'delay', 'problem', 'help', 'trouble', 'stuck', 'confusion', 
            'question', 'issue', 'bug', 'slow', 'difficulty'
        ]
        
        # Check for high priority keywords
        high_matches = [keyword for keyword in high_priority_keywords if keyword in text_lower]
        medium_matches = [keyword for keyword in medium_priority_keywords if keyword in text_lower]
        
        # Determine priority
        if high_matches:
            priority = "High"
            confidence = min(0.95, 0.7 + (len(high_matches) * 0.05))
        elif medium_matches:
            priority = "Medium"
            confidence = min(0.9, 0.6 + (len(medium_matches) * 0.05))
        else:
            priority = "Low"
            confidence = 0.7
        
        return {
            "priority": priority,
            "confidence": confidence,
            "detected_keywords": high_matches + medium_matches
        }


class CategoryAnalyzer:
    """
    Category analysis logic
    """
    
    @staticmethod
    def analyze_category(text: str) -> dict:
        """
        Analyze ticket category based on content.
        
        Args:
            text (str): Ticket text content
            
        Returns:
            dict: Category analysis results
        """
        text_lower = text.lower()
        
        # Category keywords mapping
        category_keywords = {
            "Technical Issue": ["error", "bug", "crash", "not working", "failed", "broken"],
            "Account Problem": ["login", "password", "account", "access", "authentication"],
            "Billing Question": ["payment", "billing", "invoice", "charge", "refund", "cost"],
            "Feature Request": ["feature", "enhancement", "improvement", "suggestion", "add"],
            "General Inquiry": ["question", "information", "help", "how", "what", "where"]
        }
        
        # Count keyword matches for each category
        category_scores = {}
        for category, keywords in category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                category_scores[category] = score
        
        # Determine best category
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            confidence = min(0.9, 0.5 + (category_scores[best_category] * 0.1))
        else:
            best_category = "General Inquiry"
            confidence = 0.5
        
        return {
            "category": best_category,
            "confidence": confidence
        }


@router.post("/analyze_ticket", response_model=TicketAnalysisResponse)
async def analyze_ticket(
    request: TicketAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze a support ticket for priority, category, and generate embeddings.
    
    Args:
        request: Ticket analysis request containing ticket text
        db: Database session
        
    Returns:
        TicketAnalysisResponse: Analysis results
    """
    start_time = time.time()
    
    try:
        # Validate input
        if not request.text or not request.text.strip():
            raise HTTPException(
                status_code=400,
                detail="Ticket text cannot be empty"
            )
        
        # Clean and preprocess text
        cleaned_text = TextCleaner.preprocess_for_embedding(request.text)
        
        if not cleaned_text:
            raise HTTPException(
                status_code=400,
                detail="No meaningful text content found after preprocessing"
            )
        
        # Generate embedding
        embedding_start = time.time()
        embedding_vector, embedding_metadata = embedding_service.generate_embedding(cleaned_text)
        embedding_time = (time.time() - embedding_start) * 1000
        
        # Get embedding preview (first 5 values)
        embedding_preview = embedding_service.get_embedding_preview(embedding_vector, 5)
        
        # Analyze priority
        priority_analysis = PriorityAnalyzer.analyze_priority(cleaned_text)
        
        # Analyze category
        category_analysis = CategoryAnalyzer.analyze_category(cleaned_text)
        
        # Analyze sentiment
        sentiment_analysis = TextCleaner.extract_sentiment_indicators(cleaned_text)
        
        # Detect language
        language_detection = language_service.detect_language(cleaned_text)
        
        # Generate suggested articles using recommendation service
        recommendations = recommendation_service.recommend(cleaned_text, top_k=3)
        suggested_articles = [
            rec['answer'] for rec in recommendations[:3]
        ] if recommendations else [
            f"How to resolve {category_analysis['category'].lower()}",
            f"Common {priority_analysis['priority'].lower()} priority issues",
            "General troubleshooting guide"
        ]
        
        # Calculate total processing time
        total_processing_time = (time.time() - start_time) * 1000
        
        # Create response
        response_data = {
            "priority": priority_analysis["priority"],
            "category": category_analysis["category"],
            "sentiment": sentiment_analysis["sentiment"],
            "language": language_detection,
            "confidence": priority_analysis["confidence"],
            "embedding_preview": embedding_preview,
            "detected_keywords": priority_analysis["detected_keywords"],
            "suggested_articles": suggested_articles,
            "processing_time_ms": round(total_processing_time, 2),
            "model_info": embedding_service.get_model_info()
        }
        
        # Save to database (optional - only if database is available)
        if db is not None:
            try:
                analysis_record = TicketAnalysis(
                    ticket_text=cleaned_text,
                    file_name=request.file_name,
                    priority=priority_analysis["priority"],
                    category=category_analysis["category"],
                    sentiment=sentiment_analysis["sentiment"],
                    confidence=priority_analysis["confidence"],
                    embedding_model=embedding_service.model_name,
                    embedding_values=embedding_preview,
                    detected_keywords=priority_analysis["detected_keywords"],
                    suggested_articles=suggested_articles
                )
                
                db.add(analysis_record)
                db.commit()
                
                logger.info(f"Saved analysis record with ID: {analysis_record.id}")
                
            except Exception as db_error:
                logger.error(f"Failed to save analysis to database: {str(db_error)}")
                # Don't fail the request if database save fails
        else:
            logger.debug("Database not available - skipping save operation")
        
        logger.info(f"Ticket analysis completed in {total_processing_time:.2f}ms")
        
        return TicketAnalysisResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing ticket: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze ticket: {str(e)}"
        )


@router.post("/analyze_ticket_file")
async def analyze_ticket_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Analyze a support ticket from uploaded file.
    
    Args:
        file: Uploaded file containing ticket content
        db: Database session
        
    Returns:
        TicketAnalysisResponse: Analysis results
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file size (max 5MB)
        content = await file.read()
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size exceeds 5MB limit")
        
        # Decode file content
        try:
            ticket_text = content.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="File encoding not supported. Please use UTF-8.")
        
        if not ticket_text.strip():
            raise HTTPException(status_code=400, detail="File appears to be empty")
        
        # Create request object
        request = TicketAnalysisRequest(
            text=ticket_text,
            file_name=file.filename
        )
        
        # Use the existing analyze_ticket function
        return await analyze_ticket(request, db)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing ticket file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze ticket file: {str(e)}"
        )


@router.post("/recommend", response_model=RecommendResponse)
async def recommend_articles(request: RecommendRequest):
    """
    Get top-3 similar knowledge base articles for a given query using FAISS.
    
    Args:
        request: Recommendation request containing query text
        
    Returns:
        RecommendResponse: Top recommendations with similarity scores
    """
    try:
        if not request.text or not request.text.strip():
            raise HTTPException(
                status_code=400,
                detail="Query text cannot be empty"
            )
        
        # Clean text
        cleaned_text = TextCleaner.preprocess_for_embedding(request.text)
        
        if not cleaned_text:
            raise HTTPException(
                status_code=400,
                detail="No meaningful text content found after preprocessing"
            )
        
        # Get recommendations
        recommendations = recommendation_service.recommend(cleaned_text, top_k=3)
        
        return RecommendResponse(
            recommendations=recommendations,
            query_text=cleaned_text,
            total_results=len(recommendations)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get recommendations: {str(e)}"
        )


@router.get("/topics", response_model=TopicsResponse)
async def get_topics():
    """
    Get detected topics from knowledge base using BERTopic.
    Returns top topics and content gaps for dashboard visualization.
    
    Returns:
        TopicsResponse: Topic information and content gaps
    """
    try:
        # Get knowledge base articles
        kb_articles = recommendation_service.knowledge_base
        
        if not kb_articles or len(kb_articles) < 2:
            # Return empty topics if no knowledge base
            return TopicsResponse(
                topics=[],
                total_topics=0,
                total_documents=0,
                content_gaps=[]
            )
        
        # Extract answer texts
        documents = [item.get('answer', '') for item in kb_articles if item.get('answer')]
        
        if len(documents) < 2:
            return TopicsResponse(
                topics=[],
                total_topics=0,
                total_documents=len(documents),
                content_gaps=[]
            )
        
        # Fit topics if not already fitted
        if not topic_service.topics_data or len(topic_service.documents) != len(documents):
            topic_service.fit_topics(documents)
        
        # Get top topics
        topics = topic_service.get_topics(top_n=10)
        
        # Detect content gaps
        content_gaps = topic_service.detect_content_gaps(threshold=0.1)
        
        return TopicsResponse(
            topics=topics,
            total_topics=len(topics),
            total_documents=len(documents),
            content_gaps=content_gaps[:5]  # Top 5 gaps
        )
        
    except Exception as e:
        logger.error(f"Error getting topics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get topics: {str(e)}"
        )


@router.get("/usage", response_model=UsageResponse)
async def get_usage_stats():
    """
    Get article usage statistics (most/least used articles).
    Returns mock data for dashboard visualization.
    
    Returns:
        UsageResponse: Usage statistics
    """
    try:
        # Get knowledge base
        kb_articles = recommendation_service.knowledge_base
        
        # Generate mock usage statistics
        import random
        random.seed(42)  # For consistent results
        
        usage_data = []
        for i, article in enumerate(kb_articles):
            # Mock usage count
            usage_count = random.randint(10, 1000)
            usage_data.append({
                'id': article.get('id', i + 1),
                'answer': article.get('answer', '')[:100] + '...' if len(article.get('answer', '')) > 100 else article.get('answer', ''),
                'usage_count': usage_count,
                'helpful_count': random.randint(5, usage_count),
                'last_used': datetime.utcnow().isoformat()
            })
        
        # Sort by usage
        usage_data.sort(key=lambda x: x['usage_count'], reverse=True)
        
        # Get most and least used
        most_used = usage_data[:5]
        least_used = usage_data[-5:]
        
        # Calculate stats
        total_usage = sum(item['usage_count'] for item in usage_data)
        avg_usage = total_usage / len(usage_data) if usage_data else 0
        
        usage_stats = {
            'total_usage': total_usage,
            'average_usage': round(avg_usage, 2),
            'total_articles': len(usage_data),
            'articles_above_avg': len([item for item in usage_data if item['usage_count'] > avg_usage])
        }
        
        return UsageResponse(
            most_used=most_used,
            least_used=least_used,
            total_articles=len(usage_data),
            usage_stats=usage_stats
        )
        
    except Exception as e:
        logger.error(f"Error getting usage stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get usage stats: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint for ticket service
    """
    try:
        # Test embedding service
        model_info = embedding_service.get_model_info()
        
        return {
            "status": "healthy",
            "service": "ticket-analysis",
            "model_loaded": model_info["model_loaded"],
            "model_name": model_info["model_name"],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )
