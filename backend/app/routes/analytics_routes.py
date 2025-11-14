"""
Analytics API routes for dashboard metrics
"""

import logging
from typing import Dict, List
from collections import Counter, defaultdict
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException

from app.db.database import get_db
from app.db.schemas import TicketAnalysis
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()


class AnalyticsSummaryResponse(BaseModel):
    """Response model for analytics summary."""
    ticket_count_by_priority: Dict[str, int]
    top_articles_usage: List[Dict[str, any]]
    language_distribution: List[Dict[str, any]]
    total_tickets: int


@router.get("/analytics/summary", response_model=AnalyticsSummaryResponse)
async def get_analytics_summary(
    db: Session = Depends(get_db)
):
    """
    Get analytics summary for dashboard.
    
    Returns:
        - Ticket count by priority (High/Medium/Low)
        - Top 10 recommended articles usage
        - Language distribution
    """
    if not db:
        # Return mock data if database is not available
        logger.warning("Database not available - returning mock analytics data")
        return AnalyticsSummaryResponse(
            ticket_count_by_priority={"High": 15, "Medium": 42, "Low": 28},
            top_articles_usage=[
                {"article": "How to reset password", "usage_count": 45},
                {"article": "Troubleshooting login issues", "usage_count": 38},
                {"article": "Account verification guide", "usage_count": 32},
                {"article": "Payment processing help", "usage_count": 28},
                {"article": "Feature request process", "usage_count": 25},
                {"article": "API integration guide", "usage_count": 22},
                {"article": "Data export instructions", "usage_count": 18},
                {"article": "Security best practices", "usage_count": 15},
                {"article": "Billing FAQ", "usage_count": 12},
                {"article": "General troubleshooting", "usage_count": 10},
            ],
            language_distribution=[
                {"language": "English", "count": 65, "percentage": 65.0},
                {"language": "Spanish", "count": 12, "percentage": 12.0},
                {"language": "French", "count": 10, "percentage": 10.0},
                {"language": "German", "count": 8, "percentage": 8.0},
                {"language": "Chinese", "count": 5, "percentage": 5.0},
            ],
            total_tickets=85
        )
    
    try:
        # Get all ticket analyses
        analyses = db.query(TicketAnalysis).all()
        total_tickets = len(analyses)
        
        # 1. Ticket count by priority
        priority_counter = Counter()
        for analysis in analyses:
            priority = analysis.priority or "Unknown"
            priority_counter[priority] += 1
        
        ticket_count_by_priority = {
            "High": priority_counter.get("High", 0),
            "Medium": priority_counter.get("Medium", 0),
            "Low": priority_counter.get("Low", 0)
        }
        
        # 2. Top 10 recommended articles usage
        article_counter = Counter()
        for analysis in analyses:
            if analysis.suggested_articles:
                # suggested_articles is stored as JSON (list)
                articles = analysis.suggested_articles
                if isinstance(articles, list):
                    for article in articles:
                        if article:  # Skip empty strings
                            article_counter[article] += 1
        
        # Get top 10 articles
        top_articles = article_counter.most_common(10)
        top_articles_usage = [
            {"article": article, "usage_count": count}
            for article, count in top_articles
        ]
        
        # 3. Language distribution
        language_counter = Counter()
        language_names = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ko': 'Korean',
            'pt': 'Portuguese',
            'it': 'Italian',
            'ru': 'Russian',
            'ar': 'Arabic',
            'hi': 'Hindi',
            'nl': 'Dutch',
            'sv': 'Swedish',
            'pl': 'Polish',
            'tr': 'Turkish',
        }
        
        for analysis in analyses:
            lang_code = analysis.language_code or "en"
            language_counter[lang_code] += 1
        
        # Convert to list with language names and percentages
        language_distribution = []
        if total_tickets > 0:
            for lang_code, count in language_counter.most_common(10):
                language_name = language_names.get(lang_code, lang_code.upper())
                percentage = round((count / total_tickets) * 100, 1)
                language_distribution.append({
                    "language": language_name,
                    "count": count,
                    "percentage": percentage
                })
        
        return AnalyticsSummaryResponse(
            ticket_count_by_priority=ticket_count_by_priority,
            top_articles_usage=top_articles_usage,
            language_distribution=language_distribution,
            total_tickets=total_tickets
        )
        
    except Exception as e:
        logger.error(f"Error generating analytics summary: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate analytics summary: {str(e)}"
        )

