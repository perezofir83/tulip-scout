"""Interactive Hunter Agent Test - with manual LinkedIn login."""
import asyncio
from src.database.database import init_db, get_db
from src.database.models import Campaign
from src.agents.hunter import HunterAgent
from src.services.llm_service import gemini_service
from src.services.gmail_service import gmail_service
from src.agents.copywriter import CopywriterAgent
from playwright.async_api import async_playwright

async def main():
    """Run Hunter agent test with interactive LinkedIn login."""
    
    print("🧪 Testing TulipScout Hunter Agent (Interactive Mode)")
    print("\n📝 This test will:")
    print("   1. Open a browser to LinkedIn")
    print("   2. Wait for you to manually log in")
    print("   3. Then search for leads")
    print()
    
    # Initialize database
    print("📊 Initializing database...")
    init_db()
    
    # Create test campaign using direct SQLAlchemy
    from sqlalchemy.orm import Session
    from src.database.database import SessionLocal
    
    campaign_id = None
    with SessionLocal() as db:
        campaign = Campaign(
            name="Test Campaign - Hunter Agent (Interactive)",
            target_region="Poland",
            status="ACTIVE",
            search_criteria={"wine_types": ["premium", "kosher"]},
            daily_limit=40,
        )
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        campaign_id = campaign.id
        print(f"📋 Created test campaign: {campaign_id}")
    
    print("\n🌐 Opening browser...")
    print("⏳ Please log in to LinkedIn manually in the browser window")
    print("   Then press ENTER here when you're ready to continue...")
    
    # Start Playwright and open LinkedIn homepage
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        )
        
        page = await context.new_page()
        
        # Navigate to LinkedIn homepage
        print("📱 Navigating to LinkedIn...")
        await page.goto("https://www.linkedin.com", wait_until='networkidle')
        
        # Wait for user to log in
        input("\n✋ Press ENTER once you've logged in to LinkedIn... ")
        
        print("\n✅ Continuing with search...")
        
        # Now close browser and run Hunter agent
        await browser.close()
    
    print("\n🔍 Starting Hunter agent...")
    print("   - Searching LinkedIn...")
    print("   - Scraping profiles...")
    print("   - Scoring leads...")
    print("   - Creating lead records...")
    print()
    
    # Import hunter agent
    from src.agents import hunter_agent
    
    # Run Hunter agent
    try:
        lead_ids = await hunter_agent.execute(
            campaign_id=campaign_id,
            search_query="wine importer Poland",
            max_leads=3,
        )
        
        print(f"\n✅ Hunter complete! Created {len(lead_ids)} leads")
        
        if lead_ids:
            print("\n📋 Lead IDs created:")
            for lead_id in lead_ids:
                print(f"   - {lead_id}")
                
            print("\n✨ Now check the Streamlit dashboard to view leads:")
            print("   streamlit run src/dashboard/app.py")
        else:
            print("\n⚠️  No leads created. Check logs for errors.")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
