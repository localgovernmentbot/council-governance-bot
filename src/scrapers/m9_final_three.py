"""
Final working scrapers for Yarra, Port Phillip, and Stonnington
Based on discovered URL patterns
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
from dateutil.parser import parse as parse_date
from m9_adapted import MeetingDocument, BaseM9Scraper


class YarraFinalScraper(BaseM9Scraper):
    """Yarra scraper using discovered pattern"""
    
    def __init__(self):
        super().__init__(
            council_id="YARR",
            council_name="Yarra City Council",
            base_url="https://www.yarracity.vic.gov.au"
        )
    
    def scrape(self):
        """Scrape Yarra using /sites/default/files/ pattern"""
        results = []
        
        # Strategy: Look for recent months
        current_date = datetime.now()
        
        for months_back in range(6):  # Last 6 months
            check_date = current_date - timedelta(days=30 * months_back)
            year_month = check_date.strftime("%Y-%m")
            
            # Common document patterns
            doc_patterns = [
                f"/sites/default/files/{year_month}/ordinary_council_meeting_agenda_-_tuesday_*.pdf",
                f"/sites/default/files/{year_month}/ordinary_council_meeting_minutes_-_tuesday_*.pdf",
                f"/sites/default/files/{year_month}/council_meeting_agenda_*.pdf",
                f"/sites/default/files/{year_month}/council_meeting_minutes_*.pdf",
            ]
            
            # Check meeting list page for links
            list_url = "https://www.yarracity.vic.gov.au/about-us/committees-meetings-and-minutes"
            
            try:
                response = requests.get(list_url, headers=self.headers, timeout=30)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find all PDF links
                    for link in soup.find_all('a', href=lambda x: x and f'/files/{year_month}/' in x):
                        href = link.get('href', '')
                        text = link.get_text(strip=True)
                        
                        if '.pdf' in href.lower():
                            # Extract date from filename or text
                            date_str = self.extract_date(text)
                            if not date_str:
                                # Try extracting from filename
                                date_match = re.search(r'(\d{1,2}_\w+_\d{4})', href)
                                if date_match:
                                    date_str = self.extract_date(date_match.group().replace('_', ' '))
                            
                            if date_str:
                                # Determine document type
                                doc_type = 'minutes' if 'minutes' in href.lower() else 'agenda'
                                
                                if not href.startswith('http'):
                                    href = self.base_url + href
                                
                                doc = MeetingDocument(
                                    council_id=self.council_id,
                                    council_name=self.council_name,
                                    document_type=doc_type,
                                    meeting_type='council',
                                    title=text or f"Council Meeting {doc_type.title()} - {date_str}",
                                    date=date_str,
                                    url=href,
                                    webpage_url=list_url
                                )
                                results.append(doc)
            except:
                pass
        
        # Remove duplicates and sort
        seen_urls = set()
        unique_results = []
        for doc in results:
            if doc.url not in seen_urls:
                seen_urls.add(doc.url)
                unique_results.append(doc)
        
        unique_results.sort(key=lambda x: x.date, reverse=True)
        return unique_results


class StonningtonFinalScraper(BaseM9Scraper):
    """Stonnington scraper using discovered patterns"""
    
    def __init__(self):
        super().__init__(
            council_id="STON",
            council_name="Stonnington City Council",
            base_url="https://www.stonnington.vic.gov.au"
        )
    
    def scrape(self):
        """Scrape Stonnington using /files/assets/public/ pattern"""
        results = []
        
        # Check council meetings page
        url = "https://www.stonnington.vic.gov.au/About/Council-meetings"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all links
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    # Check for PDF pattern or ZIP pattern
                    if ('/files/assets/public/' in href and '.pdf' in href) or ('/ocapi/Public/files/' in href):
                        # Extract date
                        date_str = self.extract_date(text)
                        if not date_str:
                            # Try extracting from URL
                            date_match = re.search(r'(\d{1,2}-\w{3}-\d{4})', href)
                            if date_match:
                                date_str = self.extract_date(date_match.group())
                        
                        if date_str:
                            # Determine document type
                            if '.zip' in href:
                                # ZIP usually contains multiple documents
                                doc_type = 'agenda'  # Default
                                title = text or f"Council Meeting Documents - {date_str}"
                            else:
                                doc_type = self.determine_doc_type(text) or 'agenda'
                                title = text or f"Council Meeting {doc_type.title()} - {date_str}"
                            
                            if not href.startswith('http'):
                                href = self.base_url + href
                            
                            doc = MeetingDocument(
                                council_id=self.council_id,
                                council_name=self.council_name,
                                document_type=doc_type,
                                meeting_type='council',
                                title=title,
                                date=date_str,
                                url=href,
                                webpage_url=url
                            )
                            results.append(doc)
        except Exception as e:
            print(f"  Error: {e}")
        
        # Sort by date
        results.sort(key=lambda x: x.date, reverse=True)
        return results


class PortPhillipFinalScraper(BaseM9Scraper):
    """Port Phillip scraper - needs investigation"""
    
    def __init__(self):
        super().__init__(
            council_id="PORT",
            council_name="Port Phillip City Council",
            base_url="https://www.portphillip.vic.gov.au"
        )
    
    def scrape(self):
        """Scrape Port Phillip - placeholder for now"""
        results = []
        
        # Known pattern: /about-the-council/council-meetings/YYYY-meetings-and-agendas
        # But we need to find the actual document links
        
        print("  Port Phillip still needs investigation of their specific structure")
        
        return results


# Combined test
if __name__ == "__main__":
    print("Testing Final Scrapers for Remaining 3 Councils")
    print("=" * 60)
    
    scrapers = [
        ("Yarra", YarraFinalScraper),
        ("Stonnington", StonningtonFinalScraper),
        ("Port Phillip", PortPhillipFinalScraper),
    ]
    
    total = 0
    for name, scraper_class in scrapers:
        print(f"\n{name}:")
        scraper = scraper_class()
        docs = scraper.scrape()
        print(f"  Found {len(docs)} documents")
        
        if docs:
            for doc in docs[:3]:
                print(f"  - {doc.date}: {doc.title[:50]}...")
        
        total += len(docs)
    
    print(f"\nTotal from these scrapers: {total} documents")
