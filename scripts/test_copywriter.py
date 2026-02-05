#!/usr/bin/env python3
"""
Test script for the Copywriter agent and email generation.
Creates a sample lead and generates an email draft.
"""
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.database import init_db, get_db
from src.database.models import Campaign, Lead, CampaignStatus, LeadStatus
from src.agents import copywriter_agent
from src.utils.logger import logger
import uuid


async def main():
    """Test Copywriter agent."""
    print("🧪 Testing TulipScout Copywriter Agent\n")
    
    # Initialize database
    print("📊 Initializing database...")
    init_db()
    
    # Create test campaign
    campaign_id = str(uuid.uuid4())
    print(f"📋 Creating test campaign: {campaign_id}")
    
    with get_db() as db:
        campaign = Campaign(
            id=campaign_id,
            name="Test Campaign - Eastern Europe",
            target_region="Poland",
            status=CampaignStatus.ACTIVE,
            search_criteria={"wine_types": ["premium", "kosher"]},
            daily_limit=40,
        )
        db.add(campaign)
        db.commit()
    
    # Create test lead
    lead_id = str(uuid.uuid4())
    print(f"🎯 Creating test lead: {lead_id}")
    
    website_content = """Premium Wines Distribution is Poland's leading importer of 
                sustainable and ethically-sourced wines. We specialize in organic and biodynamic 
                wines from family-owned estates. Our mission is to bring exceptional wines with 
                authentic stories to the Polish market. We focus on sustainability, quality, and 
                supporting wineries with strong ESG commitments."""
    linkedin_posts = "Recently highlighted our commitment to sustainable wine sourcing..."
    inferred_emails = ["jan.kowalski@premiumwines.pl", "info@premiumwines.pl"]
    
    with get_db() as db:
        lead = Lead(
            id=lead_id,
            campaign_id=campaign_id,
            company_name="Premium Wines Distribution Poland",
            website="https://premiumwines.pl",
            location="Warsaw, Poland",
            employee_count=25,
            decision_maker_name="Jan Kowalski",
            decision_maker_title="Chief Buyer",
            decision_maker_linkedin="https://linkedin.com/in/jan-kowalski",
            office_phone="+48 22 123 4567",
            inferred_emails=inferred_emails,
            status=LeadStatus.PENDING,
            fit_score=8.5,
            extra_data={
                "website_content": website_content,
                "linkedin_posts": linkedin_posts,
            },
        )
        db.add(lead)
        db.commit()
    
    print("\n✍️  Generating personalized email with Copywriter agent...")
    print("   - Analyzing pain points...")
    print("   - Matching to Tulip assets...")
    print("   - Generating email...")
    print("   - Creating Gmail draft...\n")
    
    try:
        email_id = await copywriter_agent.execute(
            lead_id=lead_id,
            company_name="Premium Wines Distribution Poland",
            decision_maker_name="Jan Kowalski",
            decision_maker_title="Chief Buyer",
            website_content=website_content,
            linkedin_posts=linkedin_posts,
            inferred_emails=inferred_emails,
        )
        
        print(f"✅ Email generated successfully! Email ID: {email_id}\n")
        
        # Fetch and display the email
        with get_db() as db:
            from src.database.models import Email
            email = db.query(Email).filter(Email.id == email_id).first()
            
            print("==" + "=" * 60)
            print("📧 GENERATED EMAIL")
            print("=" * 60)
            print(f"To: {inferred_emails[0]}")
            print(f"Subject: {email.subject}")
            print(f"Pain Point: {email.detected_pain_point.value}")
            print(f"Tulip Asset: {email.tulip_asset_used.value}")
            print(f"Gmail Draft ID: {email.gmail_draft_id}")
            print("\n" + "-" * 60)
            print("BODY:")
            print("-" * 60)
            print(email.body)
            print("=" * 60)
            
            print(f"\n🔗 View draft in Gmail: https://mail.google.com/mail/u/0/#drafts")
            print(f"\n✅ Test complete! Check your Gmail drafts.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error("test_failed", error=str(e))
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
