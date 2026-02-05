"""
Hunter Agent v2.0 - OSINT Search Test Script

Executes the Google OSINT search protocols and generates leads.csv
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.hunter_v2 import HunterAgentV2, OSINT_PROTOCOLS, APPROVED_COUNTRIES
from src.database.database import init_db, get_db
from src.database.models import Campaign
import uuid
import csv
import json


# Mock search function for testing (will use real search_web in production)
async def mock_search(query: str) -> str:
    """Mock search function that returns dummy results."""
    return f"Search results for: {query}\n\n[This would contain actual Google search results]"


async def main():
    """Execute Hunter v2.0 OSINT search."""
    
    print("🔍 TulipScout Hunter Agent v2.0 - Google OSINT Search")
    print("=" * 60)
    print()
    
    print("📋 Search Protocols:")
    for name, protocol in OSINT_PROTOCOLS.items():
        print(f"  • {protocol['name']}")
        print(f"    {protocol['description']}")
    print()
    
    print("🌍 Target Countries:")
    for country_name in APPROVED_COUNTRIES.keys():
        print(f"  • {country_name}")
    print()
    
    proceed = input("Execute searches? (y/n): ")
    if proceed.lower() != 'y':
        print("Aborted.")
        return
    
    # Initialize database
    print("\n📊 Initializing database...")
    init_db()
    
    # Create test campaign
    campaign_id = str(uuid.uuid4())
    with get_db() as db:
        campaign = Campaign(
            id=campaign_id,
            name="Hunter v2.0 - OSINT Test",
            target_region="Multi-Country",
            status="ACTIVE",
            search_criteria={"method": "google_osint", "protocols": list(OSINT_PROTOCOLS.keys())},
            daily_limit=100,
        )
        db.add(campaign)
        db.commit()
        print(f"✅ Campaign created: {campaign_id}")
    
    #Initialize Hunter v2.0
    hunter = HunterAgentV2(search_function=mock_search)
    
    print("\n🔎 Starting OSINT searches...")
    print("(20 total searches: 4 protocols × 5 countries)")
    print()
    
    # Execute all searches
    results = await hunter.search_all_countries()
    
    print(f"\n✅ Searches complete! {len(results)} results collected")
    
    # Save to CSV
    csv_path = Path(__file__).parent.parent / "leads.csv"
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            "Country",
            "Protocol",
            "Query",
            "Result Preview"
        ])
        
        for result in results:
            writer.writerow([
                result.get("country", ""),
                result.get("protocol", ""),
                result.get("query", ""),
                str(result.get("raw_result", ""))[:200] + "..."
            ])
    
    print(f"\n💾 Results saved to: {csv_path}")
    
    # Display summary
    print("\n" + "=" * 60)
    print("📊 SEARCH SUMMARY")
    print("=" * 60)
    
    by_country = {}
    for result in results:
        country = result.get("country", "Unknown")
        by_country[country] = by_country.get(country, 0) + 1
    
    for country, count in sorted(by_country.items()):
        print(f"  {country}: {count} searches")
    
    print("\n✨ Hunter v2.0 test complete!")
    print("\nNext steps:")
    print("  1. Review leads.csv")
    print("  2. Manually parse results into leads")
    print("  3. Or integrate with real search_web API for auto-parsing")


if __name__ == "__main__":
    asyncio.run(main())
