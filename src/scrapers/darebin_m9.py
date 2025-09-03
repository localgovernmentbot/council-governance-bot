"""
Darebin City Council Scraper for M9 Bot
Adapted from our working scraper
"""

from bs4 import BeautifulSoup
import re
from datetime import datetime
from dateutil.parser import parse as parse_date
from dataclasses import dataclass
from typing import Optional, List
import requests


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


class DarebinScraper:
    """Scraper for Darebin City Council"""
    
    def __init__(self):
        self.council_id = "DARE"
        self.council_name = "Darebin City Council"
        self.base_url = "https://www.darebin.vic.gov.au"
        # Using the specific 2025 page that has direct PDFs
        self.meetings_url = "https://www.darebin.vic.gov.au/About-council/Council-structure-and-performance/Council-and-Committee-Meetings/Council-meetings/Meeting-agendas-and-minutes/2025-Council-meeting-agendas-and-minutes"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
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
    
    def clean_title(self, title: str) -> str:
        """Clean up document titles"""
        title = re.sub(r'\(PDF,\s*[\d\.]+\s*(KB|MB|GB)\)', '', title).strip()
        title = re.sub(r'pdf\s+[\d\.]+\s*(KB|MB|GB)', '', title, flags=re.IGNORECASE).strip()
        title = re.sub(r'\.pdf$', '', title, flags=re.IGNORECASE).strip()
        return title
    
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
    
    def scrape(self):
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
                
                # Clean and parse title
                title = self.clean_title(text)
                
                # Determine document and meeting types
                doc_type = self.determine_doc_type(title)
                if not doc_type:
                    continue
                    
                meeting_type = self.determine_meeting_type(title)
                
                # Extract date
                date_str = self.extract_date(title)
                if not date_str:
                    continue
                
                # Create document record
                doc = MeetingDocument(
                    council_id=self.council_id,
                    council_name=self.council_name,
                    document_type=doc_type,
                    meeting_type=meeting_type,
                    title=title,
                    date=date_str,
                    url=href,
                    webpage_url=self.meetings_url
                )
                
                results.append(doc)
        
        # Sort by date (newest first)
        results.sort(key=lambda x: x.date, reverse=True)
        
        return results
