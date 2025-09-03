"""
Victorian Council Scraper System
Inspired by YIMBY Melbourne's approach but independently implemented
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from dateutil.parser import parse as parse_date
from dataclasses import dataclass
from typing import Optional, List
import hashlib
import json
import os


@dataclass
class ScraperReturn:
    """Data class for scraper results"""
    name: str  # Name of the meeting
    date: str  # Date in YYYY-MM-DD format
    time: str  # Time of meeting
    webpage_url: str  # URL where agenda was found
    download_url: str  # Direct URL to PDF


class BaseScraper:
    """Base class for all council scrapers"""
    
    def __init__(self, council_id: str, council_name: str, state: str, base_url: str):
        self.council_id = council_id
        self.council_name = council_name
        self.state = state
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        # Common date patterns
        self.date_patterns = [
            r'\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}',
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'\d{1,2}-\d{1,2}-\d{4}',
        ]
    
    def fetch_page(self, url: str) -> str:
        """Fetch a page with requests"""
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return ""
    
    def extract_date(self, text: str) -> Optional[str]:
        """Extract date from text and return in YYYY-MM-DD format"""
        for pattern in self.date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    parsed = parse_date(match.group())
                    return parsed.strftime('%Y-%m-%d')
                except:
                    continue
        return ""
    
    def is_future_meeting(self, date_str: str) -> bool:
        """Check if meeting date is in the future"""
        if not date_str:
            return False
        try:
            meeting_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            return meeting_date >= datetime.now().date()
        except:
            return False
    
    def scrape(self) -> List[ScraperReturn]:
        """Main scraping method - must be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement scrape()")


class MelbourneScraper(BaseScraper):
    """Scraper for City of Melbourne"""
    
    def __init__(self):
        super().__init__(
            council_id="MELB",
            council_name="City of Melbourne",
            state="VIC",
            base_url="https://www.melbourne.vic.gov.au"
        )
        self.meetings_url = "https://www.melbourne.vic.gov.au/about-council/committees-meetings/meeting-archive/pages/meeting-archive.aspx"
    
    def scrape(self) -> List[ScraperReturn]:
        """Scrape Melbourne council meetings"""
        results = []
        
        html = self.fetch_page(self.meetings_url)
        if not html:
            return results
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Melbourne uses S3 links
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Look for PDF links from S3
            if '.pdf' in href.lower() and 's3.ap-southeast-4.amazonaws.com' in href:
                # Clean title
                title = re.sub(r'pdf\s+[\d\.]+\s*(KB|MB|GB)', '', text, flags=re.IGNORECASE).strip()
                
                # Determine type
                doc_type = 'minutes' if 'MINUTES' in title.upper() else 'agenda' if 'AGENDA' in title.upper() else None
                
                if doc_type:
                    # Extract date
                    date_str = self.extract_date(title)
                    
                    results.append(ScraperReturn(
                        name=title,
                        date=date_str or "",
                        time="",  # Melbourne doesn't show times
                        webpage_url=self.meetings_url,
                        download_url=href
                    ))
        
        return results


class DarebinScraper(BaseScraper):
    """Scraper for Darebin City Council"""
    
    def __init__(self):
        super().__init__(
            council_id="DARE",
            council_name="Darebin City Council",
            state="VIC",
            base_url="https://www.darebin.vic.gov.au"
        )
        # Using the specific 2025 page that has direct PDFs
        self.meetings_url = "https://www.darebin.vic.gov.au/About-council/Council-structure-and-performance/Council-and-Committee-Meetings/Council-meetings/Meeting-agendas-and-minutes/2025-Council-meeting-agendas-and-minutes"
    
    def scrape(self) -> List[ScraperReturn]:
        """Scrape Darebin council meetings"""
        results = []
        
        html = self.fetch_page(self.meetings_url)
        if not html:
            return results
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for PDF links
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            if '.pdf' in href.lower() and any(word in text.lower() for word in ['agenda', 'minutes']):
                # Make URL absolute
                if not href.startswith('http'):
                    href = self.base_url + href if href.startswith('/') else self.base_url + '/' + href
                
                # Clean title
                title = re.sub(r'\(PDF,\s*[\d\.]+\s*(KB|MB|GB)\)', '', text).strip()
                
                # Extract date
                date_str = self.extract_date(title)
                
                results.append(ScraperReturn(
                    name=title,
                    date=date_str or "",
                    time="",
                    webpage_url=self.meetings_url,
                    download_url=href
                ))
        
        return results


# Registry of scrapers
SCRAPERS = {
    'MELB': MelbourneScraper,
    'DARE': DarebinScraper,
}


def scrape_council(council_id: str) -> List[ScraperReturn]:
    """Scrape a specific council by ID"""
    if council_id not in SCRAPERS:
        print(f"No scraper found for council: {council_id}")
        return []
    
    scraper_class = SCRAPERS[council_id]
    scraper = scraper_class()
    
    print(f"\nScraping {scraper.council_name}...")
    results = scraper.scrape()
    print(f"Found {len(results)} documents")
    
    return results


def scrape_all_councils() -> List[ScraperReturn]:
    """Scrape all registered councils"""
    all_results = []
    
    for council_id in SCRAPERS:
        results = scrape_council(council_id)
        all_results.extend(results)
    
    return all_results


if __name__ == "__main__":
    # Test the scrapers
    results = scrape_all_councils()
    
    print(f"\n\nTotal documents found: {len(results)}")
    print("\nSample results:")
    for result in results[:5]:
        print(f"\n- {result.name}")
        print(f"  Date: {result.date}")
        print(f"  URL: {result.download_url[:80]}...")
