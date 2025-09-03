"""
Hobsons Bay City Council Scraper for M9 Bot
Priority council as requested
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


class HobsonsBayScraper:
    """Scraper for Hobsons Bay City Council"""
    
    def __init__(self):
        self.council_id = "HBAY"
        self.council_name = "Hobsons Bay City Council"
        self.base_url = "https://www.hobsonsbay.vic.gov.au"
        self.meetings_url = "https://www.hobsonsbay.vic.gov.au/Council/Council-meetings/Minutes-and-agendas"
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
        """Scrape Hobsons Bay council meetings"""
        results = []
        
        # Hobsons Bay uses a per-meeting structure
        # First get the main page
        html = self.fetch_page(self.meetings_url)
        if not html:
            return results
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for meeting links
        meeting_links = []
        for link in soup.find_all('a', href=True):
            text = link.get_text(strip=True)
            href = link['href']
            
            # Look for date patterns in link text (e.g., "26 August 2025 Council Meeting")
            if self.extract_date(text) and 'meeting' in text.lower():
                # Make URL absolute
                if not href.startswith('http'):
                    href = self.base_url + href if href.startswith('/') else self.base_url + '/' + href
                
                meeting_links.append({
                    'text': text,
                    'url': href,
                    'date': self.extract_date(text)
                })
        
        # Visit each meeting page to find PDFs
        for meeting in meeting_links[:10]:  # Limit to recent meetings
            print(f"  Checking meeting: {meeting['text']}")
            
            meeting_html = self.fetch_page(meeting['url'])
            if meeting_html:
                meeting_soup = BeautifulSoup(meeting_html, 'html.parser')
                
                # Look for PDF links on the meeting page
                for pdf_link in meeting_soup.find_all('a', href=lambda x: x and '.pdf' in x.lower()):
                    pdf_text = pdf_link.get_text(strip=True)
                    pdf_href = pdf_link['href']
                    
                    # Make URL absolute
                    if not pdf_href.startswith('http'):
                        pdf_href = self.base_url + pdf_href if pdf_href.startswith('/') else self.base_url + '/' + pdf_href
                    
                    # Determine document type
                    doc_type = self.determine_doc_type(pdf_text)
                    if not doc_type:
                        continue
                    
                    # Create document
                    doc = MeetingDocument(
                        council_id=self.council_id,
                        council_name=self.council_name,
                        document_type=doc_type,
                        meeting_type=self.determine_meeting_type(meeting['text']),
                        title=f"{meeting['text']} - {doc_type.title()}",
                        date=meeting['date'],
                        url=pdf_href,
                        webpage_url=meeting['url']
                    )
                    
                    results.append(doc)
        
        # Sort by date (newest first)
        results.sort(key=lambda x: x.date, reverse=True)
        
        return results
