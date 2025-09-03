"""
M9 Council Scrapers - Base classes and registry
Adapted from our working scrapers and YIMBY Melbourne patterns
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
class MeetingDocument:
    """Data class for meeting documents"""
    council_id: str
    council_name: str
    document_type: str  # agenda, minutes
    meeting_type: str   # council, delegated, special
    title: str
    date: str          # YYYY-MM-DD format
    url: str
    webpage_url: str
    extracted_text: Optional[str] = None
    summary: Optional[str] = None
    
    def to_dict(self):
        return {
            'council_id': self.council_id,
            'council_name': self.council_name,
            'document_type': self.document_type,
            'meeting_type': self.meeting_type,
            'title': self.title,
            'date': self.date,
            'url': self.url,
            'webpage_url': self.webpage_url
        }
    
    @property
    def doc_hash(self):
        """Create unique hash for this document"""
        content = f"{self.council_id}|{self.title}|{self.url}"
        return hashlib.md5(content.encode()).hexdigest()


class BaseM9Scraper:
    """Base class for M9 council scrapers"""
    
    def __init__(self, council_id: str, council_name: str):
        self.council_id = council_id
        self.council_name = council_name
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Load council config
        with open('data/m9_councils.json', 'r') as f:
            m9_data = json.load(f)
            
        for council in m9_data['m9_councils']:
            if council['council_id'] == council_id:
                self.base_url = council['base_url']
                self.meetings_url = council['meetings_url']
                self.platform = council['platform']
                break
    
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
        date_patterns = [
            r'\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}',
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'\d{1,2}-\d{1,2}-\d{4}',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    parsed = parse_date(match.group())
                    return parsed.strftime('%Y-%m-%d')
                except:
                    continue
        return ""
    
    def determine_meeting_type(self, text: str) -> str:
        """Determine meeting type from text"""
        text_lower = text.lower()
        
        if 'delegated' in text_lower or 'committee' in text_lower:
            return 'delegated'
        elif 'special' in text_lower:
            return 'special'
        else:
            return 'council'
    
    def determine_doc_type(self, text: str) -> str:
        """Determine if document is agenda or minutes"""
        text_lower = text.lower()
        
        if 'minutes' in text_lower:
            return 'minutes'
        elif 'agenda' in text_lower:
            return 'agenda'
        else:
            return None
    
    def clean_title(self, title: str) -> str:
        """Clean up document titles"""
        # Remove file size info
        title = re.sub(r'\(PDF,\s*[\d\.]+\s*(KB|MB|GB)\)', '', title).strip()
        title = re.sub(r'pdf\s+[\d\.]+\s*(KB|MB|GB)', '', title, flags=re.IGNORECASE).strip()
        title = re.sub(r'\.pdf$', '', title, flags=re.IGNORECASE).strip()
        return title
    
    def scrape(self) -> List[MeetingDocument]:
        """Main scraping method - must be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement scrape()")


# Import specific M9 scrapers
from .m9.melbourne import MelbourneScraper
from .m9.darebin import DarebinScraper

# Registry of M9 scrapers
M9_SCRAPERS = {
    'MELB': MelbourneScraper,
    'DARE': DarebinScraper,
    # Add other M9 scrapers as we build them
}


def scrape_m9_council(council_id: str) -> List[MeetingDocument]:
    """Scrape a specific M9 council by ID"""
    if council_id not in M9_SCRAPERS:
        print(f"No scraper found for council: {council_id}")
        return []
    
    scraper_class = M9_SCRAPERS[council_id]
    scraper = scraper_class()
    
    print(f"\nScraping {scraper.council_name}...")
    results = scraper.scrape()
    print(f"Found {len(results)} documents")
    
    return results


def scrape_all_m9_councils() -> List[MeetingDocument]:
    """Scrape all M9 councils"""
    all_results = []
    
    for council_id in M9_SCRAPERS:
        results = scrape_m9_council(council_id)
        all_results.extend(results)
    
    return all_results
