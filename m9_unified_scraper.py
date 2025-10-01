#!/usr/bin/env python3
"""
Final unified M9 scraper - runs all 9 councils with timeout protection
"""

import sys
import signal
from pathlib import Path
from datetime import datetime
import json

sys.path.append('src/scrapers')

# Import working scrapers from existing modules
from melbourne_m9_v2 import MelbourneScraper
from darebin_m9 import DarebinScraper
from hobsonsbay_m9_fixed import HobsonsBayScraper
from m9_adapted import MaribyrnongScraper, MerribekScraper
from moonee_valley_fixed import MooneeValleyFixedScraper
from yarra_stonnington_fixed import YarraFixedScraper, StonningtonFixedScraper
from m9_final_three_complete import PortPhillipFinalScraper
from infocouncil_generic import InfoCouncilScraper, InfoCouncilConfig
from generic_direct import DirectPageScraper, DirectPageConfig
from generic_json import JsonListScraper, JsonListConfig


class TimeoutError(Exception):
    """Exception raised when scraping times out"""
    pass


def timeout_handler(signum, frame):
    """Handler for timeout signal"""
    raise TimeoutError("Scraping timed out")


def scrape_with_timeout(scraper_class, timeout_seconds=120):
    """
    Scrape a council with a timeout limit
    
    Args:
        scraper_class: The scraper class to instantiate and run
        timeout_seconds: Maximum seconds to allow for scraping
    
    Returns:
        List of documents or empty list if timeout/error
    """
    # Set up the timeout handler
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_seconds)
    
    try:
        scraper = scraper_class()
        docs = scraper.scrape()
        signal.alarm(0)  # Cancel the alarm
        return docs
    except TimeoutError:
        print(f"  ⏱️  TIMEOUT after {timeout_seconds}s - skipping to next council")
        signal.alarm(0)  # Cancel the alarm
        return []
    except Exception as e:
        print(f"  ❌ Error: {e}")
        signal.alarm(0)  # Cancel the alarm
        return []


print("M9 COUNCIL BOT - FINAL UNIFIED SCRAPER (v3)")
print("=" * 60)
print("⏱️  Timeout protection enabled: 120s per council")
print("🔄 Running M9 councils and additional InfoCouncil councils...")
print("✨ Using improved scrapers for Yarra and Stonnington\n")

# All 9 M9 councils
scrapers = [
    ("Melbourne", MelbourneScraper),
    ("Darebin", DarebinScraper),
    ("Hobsons Bay", HobsonsBayScraper),
    ("Maribyrnong", MaribyrnongScraper),
    ("Merri-bek", MerribekScraper),
    ("Moonee Valley", MooneeValleyFixedScraper),
    ("Yarra", YarraFixedScraper),
    ("Stonnington", StonningtonFixedScraper),
    ("Port Phillip", PortPhillipFinalScraper),
]

all_documents = []
council_stats = []
start_time = datetime.now()

for idx, (name, scraper_class) in enumerate(scrapers, 1):
    council_start = datetime.now()
    print(f"\n[{idx}/{len(scrapers)}] {name}:")
    print(f"  ⏰ Started at {council_start.strftime('%H:%M:%S')}")
    
    try:
        docs = scrape_with_timeout(scraper_class, timeout_seconds=120)
        
        # Count by type
        agendas = [d for d in docs if d.document_type == 'agenda']
        minutes = [d for d in docs if d.document_type == 'minutes']
        
        elapsed = (datetime.now() - council_start).total_seconds()
        print(f"  ⏱️  Completed in {elapsed:.1f}s")
        print(f"  📄 Total: {len(docs)} documents ({len(agendas)} agendas, {len(minutes)} minutes)")
        
        if docs:
            print(f"  📌 Most recent: {docs[0].date} - {docs[0].title[:50]}...")
            
        all_documents.extend(docs)
        council_stats.append({
            'name': name,
            'total': len(docs),
            'agendas': len(agendas),
            'minutes': len(minutes),
            'working': len(docs) > 0,
            'scrape_time': elapsed
        })
        
    except Exception as e:
        elapsed = (datetime.now() - council_start).total_seconds()
        print(f"  ❌ Error after {elapsed:.1f}s: {e}")
        council_stats.append({
            'name': name,
            'total': 0,
            'agendas': 0,
            'minutes': 0,
            'working': False,
            'scrape_time': elapsed
        })

# Registry-driven InfoCouncil councils
print("\n" + "=" * 60)
print("PROCESSING REGISTRY COUNCILS...")
print("=" * 60)

registry_path = Path('src/registry/councils.json')
if registry_path.exists():
    try:
        reg = json.loads(registry_path.read_text())
        print(f"📋 Found {len(reg)} councils in registry\n")
    except Exception as e:
        print(f"⚠️  Warning: Could not load registry: {e}")
        reg = []
        
    for idx, row in enumerate(reg, 1):
        typ = (row.get('type') or '').lower()
        council_id = row.get('id') or 'UNK'
        name = row.get('name') or council_id
        
        council_start = datetime.now()
        print(f"\n[{idx}/{len(reg)}] {name} (registry - {typ}):")
        print(f"  ⏰ Started at {council_start.strftime('%H:%M:%S')}")
        
        try:
            # Set up timeout
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(120)
            
            if typ == 'infocouncil':
                base = row.get('base') or ''
                cfg = InfoCouncilConfig(council_id=council_id, council_name=name, base_url=base, months_back=6)
                docs = InfoCouncilScraper(cfg).scrape()
            elif typ == 'direct_page':
                cfg = DirectPageConfig(council_id=council_id, council_name=name, page_url=row['page_url'], base_url=row.get('base'))
                docs = DirectPageScraper(cfg).scrape()
            elif typ == 'json_list':
                cfg = JsonListConfig(
                    council_id=council_id,
                    council_name=name,
                    endpoint=row['endpoint'],
                    item_path=row.get('item_path', []),
                    title_field=row['title_field'],
                    url_field=row['url_field'],
                    date_field=row['date_field'],
                )
                docs = JsonListScraper(cfg).scrape()
            else:
                print("  ⏭️  Skipped: unknown type")
                docs = []
            
            signal.alarm(0)  # Cancel timeout
            
            agendas = [d for d in docs if d.document_type == 'agenda']
            minutes = [d for d in docs if d.document_type == 'minutes']
            
            elapsed = (datetime.now() - council_start).total_seconds()
            print(f"  ⏱️  Completed in {elapsed:.1f}s")
            print(f"  📄 Total: {len(docs)} documents ({len(agendas)} agendas, {len(minutes)} minutes)")
            
            if docs:
                print(f"  📌 Most recent: {docs[0].date} - {docs[0].title[:50]}...")
                
            all_documents.extend(docs)
            council_stats.append({
                'name': name,
                'total': len(docs),
                'agendas': len(agendas),
                'minutes': len(minutes),
                'working': len(docs) > 0,
                'scrape_time': elapsed
            })
            
        except TimeoutError:
            signal.alarm(0)
            elapsed = (datetime.now() - council_start).total_seconds()
            print(f"  ⏱️  TIMEOUT after {elapsed:.1f}s - skipping")
            council_stats.append({
                'name': name,
                'total': 0,
                'agendas': 0,
                'minutes': 0,
                'working': False,
                'scrape_time': elapsed
            })
        except Exception as e:
            signal.alarm(0)
            elapsed = (datetime.now() - council_start).total_seconds()
            print(f"  ❌ Error after {elapsed:.1f}s: {e}")
            council_stats.append({
                'name': name,
                'total': 0,
                'agendas': 0,
                'minutes': 0,
                'working': False,
                'scrape_time': elapsed
            })

# Summary
total_elapsed = (datetime.now() - start_time).total_seconds()
print(f"\n{'='*60}")
print("FINAL SUMMARY")
print(f"{'='*60}")
print(f"⏱️  Total scraping time: {total_elapsed:.1f}s ({total_elapsed/60:.1f} minutes)")
print(f"\n✅ Working councils: {sum(1 for c in council_stats if c['working'])}/{len(council_stats)}")
print(f"📄 Total documents: {len(all_documents)}")
print(f"📋 Total agendas: {sum(c['agendas'] for c in council_stats)}")
print(f"📝 Total minutes: {sum(c['minutes'] for c in council_stats)}")

print("\n" + "-" * 60)
print("BREAKDOWN BY COUNCIL")
print("-" * 60)
for stat in sorted(council_stats, key=lambda x: x['total'], reverse=True):
    status = "✓" if stat['working'] else "✗"
    time_str = f"{stat['scrape_time']:.1f}s"
    print(f"  {status} {stat['name']:20} - {stat['total']:3} docs in {time_str:>6}")

# Save results
output_data = {
    'scrape_date': datetime.now().isoformat(),
    'total_scrape_time': total_elapsed,
    'total_councils': len(council_stats),
    'working_councils': sum(1 for c in council_stats if c['working']),
    'total_documents': len(all_documents),
    'council_stats': council_stats,
    'documents': [
        {
            'council_id': doc.council_id,
            'council_name': doc.council_name,
            'document_type': doc.document_type,
            'meeting_type': doc.meeting_type,
            'title': doc.title,
            'date': doc.date,
            'url': doc.url,
            'webpage_url': doc.webpage_url
        }
        for doc in all_documents
    ]
}

# Save to file
with open('m9_scraper_results.json', 'w') as f:
    json.dump(output_data, f, indent=2)

print(f"\n💾 Results saved to m9_scraper_results.json")

# Check if we achieved 9/9 for M9 councils
m9_working = sum(1 for c in council_stats[:9] if c['working'])
if m9_working == 9:
    print("\n🎉 " * 10)
    print("SUCCESS! ALL 9 M9 COUNCILS ARE WORKING!")
    print("🎉 " * 10)

print(f"\n📊 FINAL STATUS: {m9_working}/9 M9 councils operational")
print(f"📄 Total of {len(all_documents)} documents ready for processing")

# Exit with error if no documents were found
if len(all_documents) == 0:
    print("\n⚠️  WARNING: No documents were scraped. This may indicate a problem.")
    sys.exit(1)

# Exit successfully
print("\n✅ Scraping completed successfully!")
sys.exit(0)
