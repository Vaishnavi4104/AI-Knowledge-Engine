"""
Database schemas and models for the AI Knowledge Engine
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.database import Base


class TicketAnalysis(Base):
    """
    Model for storing ticket analysis results
    """
    __tablename__ = "ticket_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Ticket information
    ticket_text = Column(Text, nullable=False)
    file_name = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)
    
    # Analysis results
    priority = Column(String(20), nullable=False)  # High, Medium, Low
    category = Column(String(100), nullable=True)
    sentiment = Column(String(20), nullable=True)  # positive, negative, neutral
    confidence = Column(Float, nullable=False)
    language_code = Column(String(10), nullable=True)  # ISO 639-1 language code (e.g., 'en', 'es', 'fr')
    
    # Embedding information
    embedding_model = Column(String(100), default="all-MiniLM-L6-v2")
    embedding_values = Column(JSON, nullable=True)  # Store first 5 values
    
    # Keywords and suggestions
    detected_keywords = Column(JSON, nullable=True)
    suggested_articles = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_processed = Column(Boolean, default=True)


class SupportTicket(Base):
    """
    Model for storing support tickets
    """
    __tablename__ = "support_tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Ticket details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    customer_email = Column(String(255), nullable=False)
    customer_name = Column(String(255), nullable=True)
    
    # Ticket metadata
    status = Column(String(50), default="open")  # open, in_progress, resolved, closed
    priority = Column(String(20), nullable=True)  # High, Medium, Low
    category = Column(String(100), nullable=True)
    
    # Analysis reference
    analysis_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)


class KnowledgeArticle(Base):
    """
    Model for storing knowledge base articles
    """
    __tablename__ = "knowledge_articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Article content
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    
    # Categorization
    category = Column(String(100), nullable=False)
    tags = Column(JSON, nullable=True)
    
    # Embedding information
    embedding_model = Column(String(100), default="all-MiniLM-L6-v2")
    embedding_values = Column(JSON, nullable=True)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    view_count = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AnalysisLog(Base):
    """
    Model for logging analysis requests and responses
    """
    __tablename__ = "analysis_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Request information
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    request_data = Column(JSON, nullable=True)
    
    # Response information
    response_status = Column(Integer, nullable=False)
    response_data = Column(JSON, nullable=True)
    
    # Processing information
    processing_time_ms = Column(Float, nullable=True)
    embedding_time_ms = Column(Float, nullable=True)
    analysis_time_ms = Column(Float, nullable=True)
    
    # Error information
    error_message = Column(Text, nullable=True)
    
    # Metadata
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    """
    Model for storing user accounts
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User credentials
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # User information
    name = Column(String(255), nullable=False)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)