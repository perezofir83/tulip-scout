"""
CSV Viewer - Pretty Print leads.csv
"""
import csv
from pathlib import Path

def view_leads_csv():
    """Display leads.csv in a readable format."""
    
    csv_path = Path(__file__).parent.parent / "leads.csv"
    
    if not csv_path.exists():
        print("❌ leads.csv not found!")
        return
    
    print("\n" + "="*80)
    print("🔍 HUNTER V2.0 - OSINT SEARCH RESULTS")
    print("="*80 + "\n")
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        current_country = None
        count = 0
        
        for row in reader:
            country = row['country']
            
            # Print country header
            if country != current_country:
                if current_country is not None:
                    print()
                print(f"\n🌍 {country}")
                print("-" * 80)
                current_country = country
            
            count += 1
            protocol = row['protocol'].replace('_', ' ').title()
            query = row['query']
            
            print(f"\n  {count}. {protocol}")
            print(f"     Query: {query}")
            print(f"     Status: Placeholder (needs manual search execution)")
    
    print("\n" + "="*80)
    print(f"Total: {count} OSINT search queries")
    print("="*80)
    
    print("\n📝 NEXT STEPS:")
    print("  1. Copy each search query")
    print("  2. Execute manually in Google")
    print("  3. Extract company names and websites from results")
    print("  4. Update CSV with real data")
    print()

if __name__ == "__main__":
    view_leads_csv()
