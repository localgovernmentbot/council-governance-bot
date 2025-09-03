"""
Test M9 scrapers to ensure they're working
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrapers.base_m9 import scrape_all_m9_councils, M9_SCRAPERS


def test_m9_scrapers():
    """Test the M9 scrapers we have so far"""
    
    print("M9 Council Bot - Testing Scrapers")
    print("=" * 60)
    
    print(f"\nRegistered M9 scrapers: {list(M9_SCRAPERS.keys())}")
    print(f"Total: {len(M9_SCRAPERS)}/9 councils")
    
    # Test all scrapers
    all_docs = scrape_all_m9_councils()
    
    # Summary by council
    by_council = {}
    for doc in all_docs:
        if doc.council_id not in by_council:
            by_council[doc.council_id] = []
        by_council[doc.council_id].append(doc)
    
    print(f"\n\nTotal documents found: {len(all_docs)}")
    
    for council_id, docs in by_council.items():
        print(f"\n{docs[0].council_name}:")
        print(f"  Total documents: {len(docs)}")
        
        # Count by type
        agendas = [d for d in docs if d.document_type == 'agenda']
        minutes = [d for d in docs if d.document_type == 'minutes']
        
        print(f"  - Agendas: {len(agendas)}")
        print(f"  - Minutes: {len(minutes)}")
        
        # Show most recent
        if docs:
            most_recent = max(docs, key=lambda x: x.date)
            print(f"  Most recent: {most_recent.date} - {most_recent.title}")


if __name__ == "__main__":
    test_m9_scrapers()
