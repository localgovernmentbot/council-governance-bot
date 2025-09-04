"""
M9 Council Scrapers - Adapted from YIMBY Melbourne
Comprehensive scrapers that find all documents, not just the latest
"""

from bs4 import BeautifulSoup
import re
from datetime import datetime
from dateutil.parser import parse as parse_date
from dataclasses import dataclass
from typing import Optional, List
import requests
import cloudscraper


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


class BaseM9Scraper:
    """Base class for M9 scrapers"""
    
    def __init__(self, council_id: str, council_name: str, base_url: str):
        self.council_id = council_id
        self.council_name = council_name
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-AU,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        }
        # Create a Cloudscraper session to better handle 403/5xx and anti-bot
        try:
            self.session = cloudscraper.create_scraper()
            self.session.headers.update(self.headers)
        except Exception:
            self.session = requests.Session()
            self.session.headers.update(self.headers)
    
    def fetch_page(self, url: str, referer: Optional[str] = None) -> str:
        """Fetch a page using a session that can bypass simple 403s."""
        try:
            headers = dict(self.headers)
            if referer:
                headers['Referer'] = referer
            resp = self.session.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return ""

    def probe_url(self, url: str, expect_pdf: bool = True) -> bool:
        """HEAD probe to check if a URL exists (and optionally is a PDF)."""
        try:
            test_headers = dict(self.headers)
            # Use a range request to avoid full download when some hosts disallow HEAD
            test_headers['Range'] = 'bytes=0-0'
            resp = self.session.get(url, headers=test_headers, timeout=8, allow_redirects=True)
            ctype = resp.headers.get('Content-Type', '').lower()
            ok = resp.status_code in (200, 206)
            if expect_pdf:
                return ok and ('pdf' in ctype or url.lower().endswith('.pdf'))
            return ok
        except Exception:
            return False
    
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


class MaribyrnongScraper(BaseM9Scraper):
    """Maribyrnong scraper adapted from YIMBY"""
    
    def __init__(self):
        super().__init__(
            council_id="MARI",
            council_name="Maribyrnong City Council",
            base_url="https://www.maribyrnong.vic.gov.au"
        )
    
    def scrape(self):
        """Scrape all Maribyrnong meeting documents"""
        results = []
        
        # Maribyrnong's agendas and minutes page
        url = "https://www.maribyrnong.vic.gov.au/About-us/Council-and-committee-meetings/Agendas-and-minutes"
        html = self.fetch_page(url)
        
        if not html:
            return results
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find all meeting links (they use accordion triggers)
        meeting_links = soup.find_all("a", class_="accordion-trigger minutes-trigger ajax-trigger")
        
        # Process each meeting (limit to recent ones)
        for meeting_link in meeting_links[:10]:
            meeting_url = meeting_link.get('href', '')
            if not meeting_url.startswith('http'):
                meeting_url = self.base_url + meeting_url
            
            # Fetch meeting page
            meeting_html = self.fetch_page(meeting_url)
            if not meeting_html:
                continue
                
            meeting_soup = BeautifulSoup(meeting_html, 'html.parser')
            
            # Extract meeting details
            meeting_container = meeting_soup.find("div", class_="meeting-container")
            if not meeting_container:
                continue
            
            # Get date and name
            date_str = ""
            meeting_name = ""
            
            details_list = meeting_soup.find("ul", class_="content-details-list minutes-details-list")
            if details_list:
                for li in details_list.find_all("li"):
                    label = li.find("span", class_="field-label")
                    value = li.find("span", class_="field-value")
                    
                    if label and value:
                        if "Meeting Date" in label.text:
                            date_str = self.extract_date(value.text.strip())
                        elif "Meeting Type" in label.text:
                            meeting_name = value.text.strip()
            
            if not date_str:
                continue
            
            # Find documents (agenda and minutes)
            doc_divs = meeting_container.find_all("div", class_="meeting-document")
            
            for doc_div in doc_divs:
                doc_heading = doc_div.find("h2")
                if not doc_heading:
                    continue
                    
                doc_type_text = doc_heading.text.strip().lower()
                
                # Determine document type
                if 'agenda' in doc_type_text:
                    doc_type = 'agenda'
                elif 'minutes' in doc_type_text:
                    doc_type = 'minutes'
                else:
                    continue
                
                # Find PDF link
                pdf_link = doc_div.find("a", class_="document ext-pdf")
                if pdf_link and 'href' in pdf_link.attrs:
                    pdf_url = pdf_link['href']
                    if not pdf_url.startswith('http'):
                        pdf_url = self.base_url + pdf_url
                    
                    # Create document
                    doc = MeetingDocument(
                        council_id=self.council_id,
                        council_name=self.council_name,
                        document_type=doc_type,
                        meeting_type=self.determine_meeting_type(meeting_name),
                        title=f"{meeting_name} - {doc_type.title()} - {date_str}",
                        date=date_str,
                        url=pdf_url,
                        webpage_url=meeting_url
                    )
                    
                    results.append(doc)
        
        # Sort by date (newest first)
        results.sort(key=lambda x: x.date, reverse=True)
        
        return results


class MerribekScraper(BaseM9Scraper):
    """Merri-bek scraper adapted from YIMBY"""
    
    def __init__(self):
        super().__init__(
            council_id="MERR",
            council_name="Merri-bek City Council",
            base_url="https://www.merri-bek.vic.gov.au"
        )
    
    def scrape(self):
        """Scrape all Merri-bek meeting documents"""
        results = []
        
        # Merri-bek's council meeting minutes page
        url = "https://www.merri-bek.vic.gov.au/my-council/council-and-committee-meetings/council-meetings/council-meeting-minutes/"
        html = self.fetch_page(url)
        
        if not html:
            return results
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find all links that contain agenda or minutes
        all_links = soup.find_all("a", href=True)
        
        for link in all_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Check if it's a document link
            if any(word in href.lower() for word in ['agenda', 'minutes']) and '.pdf' in href.lower():
                # Determine document type
                doc_type = self.determine_doc_type(text)
                if not doc_type:
                    doc_type = self.determine_doc_type(href)
                
                if not doc_type:
                    continue
                
                # Extract date
                date_str = self.extract_date(text)
                if not date_str:
                    continue
                
                # Make URL absolute
                if not href.startswith('http'):
                    href = self.base_url + href
                
                # Get meeting type from parent heading if available
                meeting_type = 'council'
                parent = link.parent
                while parent and parent.name != 'h3':
                    parent = parent.parent
                
                if parent:
                    heading_text = parent.get_text(strip=True)
                    meeting_type = self.determine_meeting_type(heading_text)
                
                # Create document
                doc = MeetingDocument(
                    council_id=self.council_id,
                    council_name=self.council_name,
                    document_type=doc_type,
                    meeting_type=meeting_type,
                    title=text,
                    date=date_str,
                    url=href,
                    webpage_url=url
                )
                
                results.append(doc)
        
        # Sort by date (newest first)
        results.sort(key=lambda x: x.date, reverse=True)
        
        return results


# Add more scrapers as we adapt them...
