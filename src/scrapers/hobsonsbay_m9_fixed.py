"""
Hobsons Bay City Council Scraper for M9 Bot - Fixed version
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
    
    def determine_meeting_type(self, text: str) -> str:
        """Determine meeting type from text"""
        text_lower = text.lower()
        
        if 'delegated' in text_lower or 'committee' in text_lower:
            return 'delegated'
        elif 'special' in text_lower:
            return 'special'
        else:
            return 'council'
    
    def scrape(self):
        """Scrape Hobsons Bay council meetings"""
        results = []
        
        # Get the main page
        html = self.fetch_page(self.meetings_url)
        if not html:
            return results
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find links with date patterns
        date_pattern = r'\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}'
        
        meeting_links = []
        for link in soup.find_all('a', href=True):
            text = link.get_text(strip=True)
            if re.search(date_pattern, text) and 'meeting' in text.lower() and 'timetable' not in text.lower():
                href = link['href']
                if not href.startswith('http'):
                    href = self.base_url + href if href.startswith('/') else self.base_url + '/' + href
                
                meeting_links.append({
                    'text': text,
                    'url': href,
                    'date': self.extract_date(text),
                    'meeting_type': self.determine_meeting_type(text)
                })
        
        # Visit each meeting page
        for meeting in meeting_links[:10]:  # Limit to recent meetings
            print(f"  Checking: {meeting['text']}")
            
            meeting_html = self.fetch_page(meeting['url'])
            if meeting_html:
                meeting_soup = BeautifulSoup(meeting_html, 'html.parser')
                
                # Find all PDF links
                pdf_links = meeting_soup.find_all('a', href=lambda x: x and '.pdf' in x.lower())
                
                # Hobsons Bay typically has 2-3 PDFs per meeting:
                # 1. Main agenda/minutes (larger file)
                # 2. Attachments or minutes (smaller file)
                
                # Sort PDFs by file size (extracted from text)
                pdf_data = []
                for pdf in pdf_links:
                    text = pdf.get_text(strip=True)
                    href = pdf['href']
                    
                    # Extract file size if present
                    size_match = re.search(r'\((\d+(?:\.\d+)?)\s*(MB|KB)\)', text)
                    size_mb = 0
                    if size_match:
                        size = float(size_match.group(1))
                        unit = size_match.group(2)
                        size_mb = size if unit == 'MB' else size / 1024
                    
                    pdf_data.append({
                        'text': text,
                        'href': href,
                        'size_mb': size_mb
                    })
                
                # Sort by size (largest first - usually the main document)
                pdf_data.sort(key=lambda x: x['size_mb'], reverse=True)
                
                # Process PDFs
                doc_count = 0
                for i, pdf in enumerate(pdf_data):
                    # Make URL absolute
                    pdf_url = pdf['href']
                    if not pdf_url.startswith('http'):
                        pdf_url = self.base_url + pdf_url if pdf_url.startswith('/') else self.base_url + '/' + pdf_url
                    
                    # Determine document type
                    # First PDF is usually agenda/minutes, others are attachments
                    if i == 0:
                        # Main document - check if it's minutes or agenda based on date
                        # If meeting date is in the past, likely minutes; if future, agenda
                        try:
                            meeting_date = datetime.strptime(meeting['date'], '%Y-%m-%d')
                            if meeting_date.date() < datetime.now().date():
                                doc_type = 'minutes'
                            else:
                                doc_type = 'agenda'
                        except:
                            doc_type = 'agenda'  # Default to agenda
                        
                        title = f"{meeting['text']} - {doc_type.title()}"
                    else:
                        # Attachments
                        if 'attachment' in pdf['text'].lower():
                            continue  # Skip attachments for now
                        else:
                            # Could be minutes if there's also an agenda
                            doc_type = 'minutes' if doc_count == 1 else 'agenda'
                            title = f"{meeting['text']} - {doc_type.title()}"
                    
                    # Create document
                    doc = MeetingDocument(
                        council_id=self.council_id,
                        council_name=self.council_name,
                        document_type=doc_type,
                        meeting_type=meeting['meeting_type'],
                        title=title,
                        date=meeting['date'],
                        url=pdf_url,
                        webpage_url=meeting['url']
                    )
                    
                    results.append(doc)
                    doc_count += 1
        
        # Sort by date (newest first)
        results.sort(key=lambda x: x.date, reverse=True)
        
        return results
