"""
Melbourne City Council Scraper for M9 Bot - Fixed for their date format
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


class MelbourneScraper:
    """Scraper for City of Melbourne"""
    
    def __init__(self):
        self.council_id = "MELB"
        self.council_name = "City of Melbourne"
        self.base_url = "https://www.melbourne.vic.gov.au"
        self.meetings_url = "https://www.melbourne.vic.gov.au/about-council/committees-meetings/meeting-archive/pages/meeting-archive.aspx"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Month abbreviations used by Melbourne
        self.month_map = {
            'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04',
            'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08',
            'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'
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
    
    def extract_date_melbourne(self, text: str) -> Optional[str]:
        """Extract date from Melbourne's format (e.g., AUG25, JUL25)"""
        # Look for pattern like AUG25, JUL25
        match = re.search(r'([A-Z]{3})(\d{2})', text)
        if match:
            month_abbr = match.group(1)
            year_short = match.group(2)
            
            if month_abbr in self.month_map:
                month = self.month_map[month_abbr]
                # Assume 20XX for year
                year = f"20{year_short}"
                # Use first day of month since we don't have specific date
                return f"{year}-{month}-01"
        
        return ""
    
    def determine_meeting_type(self, text: str) -> str:
        """Determine meeting type from text"""
        text_upper = text.upper()
        
        # Melbourne uses CCL for Council, FMC for Future Melbourne Committee
        if 'FMC' in text_upper:
            return 'delegated'
        elif 'CCL' in text_upper:
            return 'council'
        elif 'SPECIAL' in text_upper:
            return 'special'
        else:
            return 'council'
    
    def determine_doc_type(self, text: str) -> str:
        """Determine if document is agenda or minutes"""
        text_upper = text.upper()
        
        if 'MINUTES' in text_upper:
            return 'minutes'
        elif 'AGENDA' in text_upper:
            return 'agenda'
        elif 'RESOLUTIONS' in text_upper:
            return None  # Skip resolutions for now
        else:
            return None
    
    def clean_melbourne_title(self, text: str) -> str:
        """Clean Melbourne's title format"""
        # Remove file size
        text = re.sub(r'(pdf|doc)\s+[\d\.]+\s*(KB|MB)', '', text, flags=re.IGNORECASE).strip()
        
        # Expand abbreviations
        text = text.replace('CCL', 'Council')
        text = text.replace('FMC', 'Future Melbourne Committee')
        
        # Add spaces between parts
        text = re.sub(r'([A-Z]{3}\d{2})\s*', r'\1 ', text)
        
        return text.strip()
    
    def scrape(self):
        """Scrape Melbourne council meetings"""
        results = []
        
        html = self.fetch_page(self.meetings_url)
        if not html:
            return results
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for S3 links and PDFs
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Check if it's a document link
            is_document = False
            if '.pdf' in href.lower() or '.doc' in href.lower():
                if 's3' in href.lower() and 'amazonaws' in href.lower():
                    is_document = True
            
            if is_document:
                # Skip resolutions
                if 'RESOLUTIONS' in text.upper():
                    continue
                
                # Determine document type
                doc_type = self.determine_doc_type(text)
                if not doc_type:
                    continue
                
                # Extract date
                date_str = self.extract_date_melbourne(text)
                if not date_str:
                    continue
                
                # Determine meeting type
                meeting_type = self.determine_meeting_type(text)
                
                # Clean title
                title = self.clean_melbourne_title(text)
                
                # Make sure URL is absolute
                if not href.startswith('http'):
                    if href.startswith('//'):
                        href = 'https:' + href
                    elif href.startswith('/'):
                        href = self.base_url + href
                
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
