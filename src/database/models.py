"""Database models for TulipScout."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, ForeignKey, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class CampaignStatus(str, enum.Enum):
    """Campaign status enum."""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"


class LeadStatus(str, enum.Enum):
    """Lead status enum."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONTACTED = "contacted"


class EmailStatus(str, enum.Enum):
    """Email status enum."""
    DRAFT = "draft"
    SENT = "sent"
    BOUNCED = "bounced"
    REPLIED = "replied"


class PainPoint(str, enum.Enum):
    """Pain point categories."""
    ESG = "ESG"
    INNOVATION = "Innovation"
    QUALITY = "Quality"
    UNKNOWN = "Unknown"


class TulipAsset(str, enum.Enum):
    """Tulip Winery assets."""
    VILLAGE_OF_HOPE = "Village_of_Hope"
    AGTECH = "AgTech"
    ACCOLADES = "Accolades"


class Campaign(Base):
    """Campaign model."""
    __tablename__ = "campaigns"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    target_region = Column(String, nullable=False)
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT)
    search_criteria = Column(JSON)  # Wine types, company size, etc.
    daily_limit = Column(Integer, default=40)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    leads = relationship("Lead", back_populates="campaign", cascade="all, delete-orphan")


class Lead(Base):
    """Lead model."""
    __tablename__ = "leads"
    
    id = Column(String, primary_key=True)
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=False)
    
    # Company information
    company_name = Column(String, nullable=False)
    website = Column(String)
    location = Column(String)
    employee_count = Column(Integer)
    
    # Decision maker
    decision_maker_name = Column(String)
    decision_maker_title = Column(String)
    decision_maker_linkedin = Column(String)
    
    # Contact information
    office_phone = Column(String)
    email_pattern = Column(String)  # e.g., "firstname.lastname@domain.com"
    inferred_emails = Column(JSON)  # Array of calculated email guesses
    
    # Scoring
    fit_score = Column(Float)  # 0-10 AI confidence
    
    # Status
    status = Column(Enum(LeadStatus), default=LeadStatus.PENDING)
    
    # Raw data
    extra_data = Column(JSON)  # Stores raw scraped data
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="leads")
    emails = relationship("Email", back_populates="lead", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="lead", cascade="all, delete-orphan")


class Email(Base):
    """Email model."""
    __tablename__ = "emails"
    
    id = Column(String, primary_key=True)
    lead_id = Column(String, ForeignKey("leads.id"), nullable=False)
    
    subject = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    
    # Pain-point matching
    detected_pain_point = Column(Enum(PainPoint))
    tulip_asset_used = Column(Enum(TulipAsset))
    
    # Gmail integration
    gmail_draft_id = Column(String)
    
    # Status
    status = Column(Enum(EmailStatus), default=EmailStatus.DRAFT)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime)
    replied_at = Column(DateTime)
    
    # Relationships
    lead = relationship("Lead", back_populates="emails")


class Activity(Base):
    """Activity log model for audit trail."""
    __tablename__ = "activities"
    
    id = Column(String, primary_key=True)
    lead_id = Column(String, ForeignKey("leads.id"), nullable=False)
    
    agent_name = Column(String, nullable=False)  # Hunter, Copywriter, Manager
    action = Column(String, nullable=False)  # scraped, scored, drafted, sent
    details = Column(JSON)  # Additional context
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    lead = relationship("Lead", back_populates="activities")
