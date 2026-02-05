"""FastAPI main application."""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime

from src.database.database import get_db_session, init_db
from src.database.models import Campaign, Lead, Email, CampaignStatus, LeadStatus
from src.agents import copywriter_agent, hunter_agent
from src.utils.logger import logger
from pydantic import BaseModel


# Pydantic models for API
class CampaignCreate(BaseModel):
    """Campaign creation request."""
    name: str
    target_region: str
    search_criteria: dict = {}
    daily_limit: int = 40


class LeadCreate(BaseModel):
    """Lead creation request."""
    campaign_id: str
    company_name: str
    website: str
    location: str
    employee_count: int | None = None
    decision_maker_name: str
    decision_maker_title: str
    decision_maker_linkedin: str | None = None
    office_phone: str | None = None
    inferred_emails: List[str] = []
    extra_data: dict = {}


class EmailGenerate(BaseModel):
    """Email generation request."""
    lead_id: str


class HuntLeads(BaseModel):
    """Hunt leads request."""
    campaign_id: str
    search_query: str
    max_leads: int = 10
    region: str = "Eastern_Europe"


# Initialize FastAPI app
app = FastAPI(
    title="TulipScout API",
    description="B2B Lead Generation System for Tulip Winery",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    logger.info("api_started")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "TulipScout API"}


@app.get("/health")
async def health():
    """Health check with detailed status."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }


# Campaign endpoints
@app.post("/campaigns", response_model=dict)
async def create_campaign(
    campaign: CampaignCreate,
    db: Session = Depends(get_db_session),
):
    """Create a new campaign."""
    campaign_id = str(uuid.uuid4())
    
    db_campaign = Campaign(
        id=campaign_id,
        name=campaign.name,
        target_region=campaign.target_region,
        search_criteria=campaign.search_criteria,
        daily_limit=campaign.daily_limit,
        status=CampaignStatus.DRAFT,
    )
    
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    
    logger.info("campaign_created", campaign_id=campaign_id, name=campaign.name)
    
    return {
        "id": campaign_id,
        "name": campaign.name,
        "status": campaign.status,
    }


@app.get("/campaigns")
async def list_campaigns(db: Session = Depends(get_db_session)):
    """List all campaigns."""
    campaigns = db.query(Campaign).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "target_region": c.target_region,
            "status": c.status.value,
            "created_at": c.created_at.isoformat(),
        }
        for c in campaigns
    ]


@app.get("/campaigns/{campaign_id}")
async def get_campaign(campaign_id: str, db: Session = Depends(get_db_session)):
    """Get campaign details."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return {
        "id": campaign.id,
        "name": campaign.name,
        "target_region": campaign.target_region,
        "status": campaign.status.value,
        "daily_limit": campaign.daily_limit,
        "lead_count": len(campaign.leads),
        "created_at": campaign.created_at.isoformat(),
    }


# Lead endpoints
@app.post("/leads", response_model=dict)
async def create_lead(
    lead: LeadCreate,
    db: Session = Depends(get_db_session),
):
    """Create a new lead."""
    lead_id = str(uuid.uuid4())
    
    db_lead = Lead(
        id=lead_id,
        campaign_id=lead.campaign_id,
        company_name=lead.company_name,
        website=lead.website,
        location=lead.location,
        employee_count=lead.employee_count,
        decision_maker_name=lead.decision_maker_name,
        decision_maker_title=lead.decision_maker_title,
        decision_maker_linkedin=lead.decision_maker_linkedin,
        office_phone=lead.office_phone,
        inferred_emails=lead.inferred_emails,
        extra_data=lead.extra_data,
        status=LeadStatus.PENDING,
        fit_score=5.0,  # Default score
    )
    
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    
    logger.info("lead_created", lead_id=lead_id, company=lead.company_name)
    
    return {
        "id": lead_id,
        "company_name": lead.company_name,
        "status": db_lead.status.value,
    }


@app.get("/leads")
async def list_leads(
    campaign_id: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db_session),
):
    """List leads with optional filters."""
    query = db.query(Lead)
    
    if campaign_id:
        query = query.filter(Lead.campaign_id == campaign_id)
    if status:
        query = query.filter(Lead.status == status)
    
    leads = query.all()
    
    return [
        {
            "id": l.id,
            "company_name": l.company_name,
            "location": l.location,
            "decision_maker_name": l.decision_maker_name,
            "decision_maker_title": l.decision_maker_title,
            "fit_score": l.fit_score,
            "status": l.status.value,
            "email_count": len(l.emails),
            "created_at": l.created_at.isoformat(),
        }
        for l in leads
    ]


@app.get("/leads/{lead_id}")
async def get_lead(lead_id: str, db: Session = Depends(get_db_session)):
    """Get lead details."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    return {
        "id": lead.id,
        "company_name": lead.company_name,
        "website": lead.website,
        "location": lead.location,
        "employee_count": lead.employee_count,
        "decision_maker_name": lead.decision_maker_name,
        "decision_maker_title": lead.decision_maker_title,
        "decision_maker_linkedin": lead.decision_maker_linkedin,
        "inferred_emails": lead.inferred_emails,
        "fit_score": lead.fit_score,
        "status": lead.status.value,
        "emails": [
            {
                "id": e.id,
                "subject": e.subject,
                "status": e.status.value,
                "created_at": e.created_at.isoformat(),
            }
            for e in lead.emails
        ],
        "created_at": lead.created_at.isoformat(),
    }


@app.patch("/leads/{lead_id}/approve")
async def approve_lead(lead_id: str, db: Session = Depends(get_db_session)):
    """Approve a lead."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    lead.status = LeadStatus.APPROVED
    db.commit()
    
    logger.info("lead_approved", lead_id=lead_id)
    
    return {"id": lead_id, "status": "approved"}


# Email endpoints
@app.post("/emails/generate")
async def generate_email(
    request: EmailGenerate,
    db: Session = Depends(get_db_session),
):
    """Generate email for a lead using Copywriter agent."""
    lead = db.query(Lead).filter(Lead.id == request.lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    try:
        # Use Copywriter agent to generate email
        email_id = await copywriter_agent.execute(
            lead_id=lead.id,
            company_name=lead.company_name,
            decision_maker_name=lead.decision_maker_name,
            decision_maker_title=lead.decision_maker_title,
            website_content=lead.extra_data.get("website_content", "") if lead.extra_data else "",
            linkedin_posts=lead.extra_data.get("linkedin_posts") if lead.extra_data else None,
            inferred_emails=lead.inferred_emails,
        )
        
        # Refresh to get the created email
        db.refresh(lead)
        email = db.query(Email).filter(Email.id == email_id).first()
        
        return {
            "id": email.id,
            "subject": email.subject,
            "body": email.body,
            "pain_point": email.detected_pain_point.value,
            "tulip_asset": email.tulip_asset_used.value,
            "gmail_draft_id": email.gmail_draft_id,
            "status": email.status.value,
        }
        
    except Exception as e:
        logger.error("email_generation_failed", lead_id=request.lead_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/emails/{email_id}")
async def get_email(email_id: str, db: Session = Depends(get_db_session)):
    """Get email details."""
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    return {
        "id": email.id,
        "lead_id": email.lead_id,
        "subject": email.subject,
        "body": email.body,
        "pain_point": email.detected_pain_point.value if email.detected_pain_point else None,
        "tulip_asset": email.tulip_asset_used.value if email.tulip_asset_used else None,
        "gmail_draft_id": email.gmail_draft_id,
        "status": email.status.value,
        "created_at": email.created_at.isoformat(),
    }


# Hunter agent endpoint
@app.post("/hunt")
async def hunt_leads(
    request: HuntLeads,
    db: Session = Depends(get_db_session),
):
    """
    Hunt for leads using Playwright + LinkedIn scraping.
    This is an async operation - returns immediately with job status.
    """
    campaign = db.query(Campaign).filter(Campaign.id == request.campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    try:
        # Run Hunter agent
        lead_ids = await hunter_agent.execute(
            campaign_id=request.campaign_id,
            search_query=request.search_query,
            max_leads=request.max_leads,
            region=request.region,
        )
        
        logger.info(
            "hunt_complete",
            campaign_id=request.campaign_id,
            leads_created=len(lead_ids),
        )
        
        return {
            "status": "success",
            "campaign_id": request.campaign_id,
            "leads_created": len(lead_ids),
            "lead_ids": lead_ids,
        }
        
    except Exception as e:
        logger.error("hunt_failed", campaign_id=request.campaign_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

