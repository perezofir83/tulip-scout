#!/usr/bin/env python3
"""
Test script for the Hunter agent.
Searches LinkedIn and creates leads.
"""
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.database import init_db, get_db
from src.database.models import Campaign, CampaignStatus
from src.agents import hunter_agent
from src.utils.logger import logger
import uuid


async def main():
    """Test Hunter agent."""
    print("🧪 Testing TulipScout Hunter Agent\n")
    print("⚠️  WARNING: This will open a browser and search LinkedIn")
    print("   You may need to log in to LinkedIn manually\n")
    
    proceed = input("Continue? (y/n): ")
    if proceed.lower() != 'y':
        print("Aborted.")
        return 1
    
    # Initialize database
    print("\n📊 Initializing database...")
    init_db()
    
    # Create test campaign
    campaign_id = str(uuid.uuid4())
    print(f"📋 Creating test campaign: {campaign_id}")
    
    with get_db() as db:
        campaign = Campaign(
            id=campaign_id,
            name="Test Campaign - Hunter Agent",
            target_region="Poland",
            status=CampaignStatus.ACTIVE,
            search_criteria={"wine_types": ["premium", "kosher"]},
            daily_limit=40,
        )
        db.add(campaign)
        db.commit()
    
    print("\n🔍 Starting Hunter agent...")
    print("   - Searching LinkedIn...")
    print("   - Scraping profiles...")
    print("   - Scoring leads...")
    print("   - Creating lead records...\n")
    
    try:
        # Run Hunter
        search_query = "wine importer Poland"
        max_leads = 3  # Start small for testing
        
        lead_ids = await hunter_agent.execute(
            campaign_id=campaign_id,
            search_query=search_query,
            max_leads=max_leads,
            region="Eastern_Europe",
        )
        
        print(f"\n✅ Hunter complete! Created {len(lead_ids)} leads\n")
        
        # Display created leads
        if lead_ids:
            print("=" * 60)
            print("📊 CREATED LEADS")
            print("=" * 60)
            
            with get_db() as db:
                from src.database.models import Lead
                
                for lead_id in lead_ids:
                    lead = db.query(Lead).filter(Lead.id == lead_id).first()
                    
                    print(f"\n🏢 {lead.company_name}")
                    print(f"   Location: {lead.location}")
                    print(f"   Decision Maker: {lead.decision_maker_name} ({lead.decision_maker_title})")
                    print(f"   Fit Score: {lead.fit_score}/10")
                    print(f"   LinkedIn: {lead.decision_maker_linkedin}")
                    print(f"   Inferred Emails: {', '.join(lead.inferred_emails[:3])}")
                    print(f"   Status: {lead.status.value}")
            
            print("\n" + "=" * 60)
            print(f"\n✅ Test complete! View leads in dashboard:")
            print(f"   streamlit run dashboard/app.py")
        else:
            print("⚠️  No leads created. Check logs for errors.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error("test_failed", error=str(e))
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
