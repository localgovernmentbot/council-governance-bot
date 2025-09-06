#!/usr/bin/env python3
"""
Universal Victorian Council Scraper - Supports all 79 councils
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Add scrapers to path
sys.path.append('src/scrapers')

# Import existing M9 scrapers
from melbourne_m9_v2 import MelbourneScraper
from darebin_m9 import DarebinScraper
from hobsonsbay_m9_fixed import HobsonsBayScraper
from m9_adapted import MaribyrnongScraper, MerribekScraper
from moonee_valley_fixed import MooneeValleyFixedScraper
from yarra_stonnington_fixed import YarraFixedScraper, StonningtonFixedScraper
from m9_final_three_complete import PortPhillipFinalScraper

# Import generic scrapers
from infocouncil_generic import InfoCouncilScraper, InfoCouncilConfig
from generic_direct import DirectPageScraper, DirectPageConfig
from generic_json import JsonListScraper, JsonListConfig
from generic_web import GenericCouncilScraper, SmartCouncilScraper

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VictorianCouncilScraper:
    """Universal scraper for all 79 Victorian councils"""
    
    def __init__(self, registry_path='src/registry/all_councils.json'):
        """Initialize with council registry"""
        self.registry_path = Path(registry_path)
        self.councils = self._load_registry()
        self.results = []
        self.stats = []
        
    def _load_registry(self) -> List[Dict]:
        """Load council registry"""
        if not self.registry_path.exists():
            logger.error(f"Registry not found: {self.registry_path}")
            return []
        
        with open(self.registry_path) as f:
            data = json.load(f)
            return data.get('councils', [])
    
    def scrape_council(self, council: Dict) -> List:
        """Scrape a single council based on its configuration"""
        council_id = council.get('id')
        council_name = council.get('name')
        council_type = council.get('type', 'generic')
        
        logger.info(f"Scraping {council_name} ({council_type})...")
        
        try:
            # M9 councils with custom scrapers
            if council_type == 'm9':
                scraper_name = council.get('scraper')
                if scraper_name == 'MelbourneScraper':
                    scraper = MelbourneScraper()
                elif scraper_name == 'DarebinScraper':
                    scraper = DarebinScraper()
                elif scraper_name == 'HobsonsBayScraper':
                    scraper = HobsonsBayScraper()
                elif scraper_name == 'MaribyrnongScraper':
                    scraper = MaribyrnongScraper()
                elif scraper_name == 'MerribekScraper':
                    scraper = MerribekScraper()
                elif scraper_name == 'MooneeValleyFixedScraper':
                    scraper = MooneeValleyFixedScraper()
                elif scraper_name == 'YarraFixedScraper':
                    scraper = YarraFixedScraper()
                elif scraper_name == 'StonningtonFixedScraper':
                    scraper = StonningtonFixedScraper()
                elif scraper_name == 'PortPhillipFinalScraper':
                    scraper = PortPhillipFinalScraper()
                else:
                    logger.warning(f"Unknown M9 scraper: {scraper_name}")
                    return []
                
                return scraper.scrape()
            
            # InfoCouncil-based councils
            elif council_type == 'infocouncil':
                base_url = council.get('base_url', '')
                config = InfoCouncilConfig(
                    council_id=council_id,
                    council_name=council_name,
                    base_url=base_url,
                    months_back=6
                )
                scraper = InfoCouncilScraper(config)
                return scraper.scrape()
            
            # Direct page scrapers
            elif council_type == 'direct_page':
                config = DirectPageConfig(
                    council_id=council_id,
                    council_name=council_name,
                    page_url=council.get('meeting_url'),
                    base_url=council.get('base_url')
                )
                scraper = DirectPageScraper(config)
                return scraper.scrape()
            
            # JSON API scrapers
            elif council_type == 'json_list':
                config = JsonListConfig(
                    council_id=council_id,
                    council_name=council_name,
                    endpoint=council.get('endpoint'),
                    item_path=council.get('item_path', []),
                    title_field=council.get('title_field'),
                    url_field=council.get('url_field'),
                    date_field=council.get('date_field')
                )
                scraper = JsonListScraper(config)
                return scraper.scrape()
            
            # Generic scrapers - try to auto-detect
            else:
                # Try generic scraping based on URL patterns
                return self._generic_scrape(council)
            
        except Exception as e:
            logger.error(f"Error scraping {council_name}: {e}")
            return []
    
    def _generic_scrape(self, council: Dict) -> List:
        """Generic scraping for councils without specific scrapers"""
        council_id = council.get('id')
        council_name = council.get('name')
        meeting_url = council.get('meeting_url')
        hashtag = council.get('hashtag')
        
        if not meeting_url:
            logger.warning(f"No meeting URL for {council_name}")
            return []
        
        # Use SmartCouncilScraper for better detection
        scraper = SmartCouncilScraper(
            council_id=council_id,
            council_name=council_name,
            meeting_url=meeting_url,
            hashtag=hashtag
        )
        
        return scraper.scrape()
    
    def scrape_all(self, limit: Optional[int] = None) -> Dict:
        """Scrape all councils (or up to limit)"""
        councils_to_scrape = self.councils[:limit] if limit else self.councils
        
        logger.info(f"Starting scrape of {len(councils_to_scrape)} councils...")
        
        all_documents = []
        
        for council in councils_to_scrape:
            council_name = council.get('name')
            
            try:
                docs = self.scrape_council(council)
                
                # Count by type
                agendas = [d for d in docs if hasattr(d, 'document_type') and d.document_type == 'agenda']
                minutes = [d for d in docs if hasattr(d, 'document_type') and d.document_type == 'minutes']
                
                logger.info(f"{council_name}: {len(docs)} documents ({len(agendas)} agendas, {len(minutes)} minutes)")
                
                all_documents.extend(docs)
                
                self.stats.append({
                    'id': council.get('id'),
                    'name': council_name,
                    'region': council.get('region'),
                    'total': len(docs),
                    'agendas': len(agendas),
                    'minutes': len(minutes),
                    'working': len(docs) > 0,
                    'hashtag': council.get('hashtag')
                })
                
            except Exception as e:
                logger.error(f"Failed to scrape {council_name}: {e}")
                
                self.stats.append({
                    'id': council.get('id'),
                    'name': council_name,
                    'region': council.get('region'),
                    'total': 0,
                    'agendas': 0,
                    'minutes': 0,
                    'working': False,
                    'error': str(e),
                    'hashtag': council.get('hashtag')
                })
        
        # Prepare results
        self.results = {
            'scrape_date': datetime.now().isoformat(),
            'total_councils': len(councils_to_scrape),
            'working_councils': sum(1 for s in self.stats if s['working']),
            'total_documents': len(all_documents),
            'council_stats': self.stats,
            'documents': self._serialize_documents(all_documents)
        }
        
        return self.results
    
    def _serialize_documents(self, documents: List) -> List[Dict]:
        """Convert document objects to JSON-serializable format"""
        serialized = []
        
        for doc in documents:
            if hasattr(doc, '__dict__'):
                # Object with attributes
                doc_dict = {
                    'council_id': getattr(doc, 'council_id', ''),
                    'council_name': getattr(doc, 'council_name', ''),
                    'document_type': getattr(doc, 'document_type', ''),
                    'meeting_type': getattr(doc, 'meeting_type', ''),
                    'title': getattr(doc, 'title', getattr(doc, 'name', '')),
                    'date': getattr(doc, 'date', ''),
                    'url': getattr(doc, 'url', getattr(doc, 'download_url', '')),
                    'webpage_url': getattr(doc, 'webpage_url', '')
                }
            else:
                # Already a dict
                doc_dict = doc
            
            serialized.append(doc_dict)
        
        return serialized
    
    def save_results(self, output_path='all_councils_results.json'):
        """Save scraping results to JSON file"""
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"Results saved to {output_path}")
    
    def print_summary(self):
        """Print summary of scraping results"""
        if not self.stats:
            print("No results to summarize")
            return
        
        print(f"\n{'='*60}")
        print("SCRAPING SUMMARY:")
        print(f"\nTotal councils scraped: {len(self.stats)}")
        print(f"Working councils: {sum(1 for s in self.stats if s['working'])}")
        print(f"Total documents: {sum(s['total'] for s in self.stats)}")
        print(f"Total agendas: {sum(s['agendas'] for s in self.stats)}")
        print(f"Total minutes: {sum(s['minutes'] for s in self.stats)}")
        
        # By region
        regions = {}
        for stat in self.stats:
            region = stat.get('region', 'Unknown')
            if region not in regions:
                regions[region] = {'total': 0, 'working': 0}
            regions[region]['total'] += 1
            if stat['working']:
                regions[region]['working'] += 1
        
        print("\nBy Region:")
        for region, counts in sorted(regions.items()):
            print(f"  {region}: {counts['working']}/{counts['total']} working")
        
        # Top councils
        print("\nTop 10 Councils by Documents:")
        sorted_stats = sorted(self.stats, key=lambda x: x['total'], reverse=True)
        for stat in sorted_stats[:10]:
            status = "✓" if stat['working'] else "✗"
            print(f"  {status} {stat['name']:30} - {stat['total']:3} documents")
        
        # Failed councils
        failed = [s for s in self.stats if not s['working']]
        if failed:
            print(f"\nFailed Councils ({len(failed)}):")
            for stat in failed[:10]:
                error = stat.get('error', 'Unknown error')[:50]
                print(f"  {stat['name']:30} - {error}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrape Victorian Council documents')
    parser.add_argument('--limit', type=int, help='Limit number of councils to scrape')
    parser.add_argument('--council', help='Scrape specific council by ID')
    parser.add_argument('--output', default='all_councils_results.json', help='Output file path')
    parser.add_argument('--m9-only', action='store_true', help='Only scrape M9 councils')
    
    args = parser.parse_args()
    
    scraper = VictorianCouncilScraper()
    
    if args.council:
        # Scrape single council
        council = next((c for c in scraper.councils if c['id'] == args.council), None)
        if council:
            docs = scraper.scrape_council(council)
            print(f"Scraped {len(docs)} documents from {council['name']}")
        else:
            print(f"Council not found: {args.council}")
    
    elif args.m9_only:
        # Only scrape M9 councils
        m9_councils = [c for c in scraper.councils if c.get('type') == 'm9']
        scraper.councils = m9_councils
        scraper.scrape_all()
        scraper.save_results('m9_results.json')
    
    else:
        # Scrape all or limited councils
        scraper.scrape_all(limit=args.limit)
        scraper.save_results(args.output)
    
    scraper.print_summary()


if __name__ == '__main__':
    main()
