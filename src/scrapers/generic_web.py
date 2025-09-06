"""
Generic web scraper for Victorian councils
Handles common meeting page patterns
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """Standard document structure"""
    council_id: str
    council_name: str
    document_type: str  # 'agenda' or 'minutes'
    meeting_type: str
    title: str
    date: str
    url: str
    webpage_url: str = ''


class GenericCouncilScraper:
    """Generic scraper that handles common council website patterns"""
    
    def __init__(self, council_id: str, council_name: str, meeting_url: str, hashtag: str = None):
        self.council_id = council_id
        self.council_name = council_name
        self.meeting_url = meeting_url
        self.hashtag = hashtag or council_id
        self.base_url = self._get_base_url(meeting_url)
        
    def _get_base_url(self, url: str) -> str:
        """Extract base URL from meeting URL"""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    
    def scrape(self) -> List[Document]:
        """Main scraping method"""
        try:
            response = requests.get(self.meeting_url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            documents = []
            
            # Try multiple patterns
            documents.extend(self._find_pdf_links(soup))
            documents.extend(self._find_meeting_lists(soup))
            documents.extend(self._find_table_rows(soup))
            documents.extend(self._find_infocouncil_pattern(soup))
            
            # Deduplicate by URL
            seen_urls = set()
            unique_docs = []
            for doc in documents:
                if doc.url not in seen_urls:
                    seen_urls.add(doc.url)
                    unique_docs.append(doc)
            
            return unique_docs
            
        except Exception as e:
            logger.error(f"Error scraping {self.council_name}: {e}")
            return []
    
    def _find_pdf_links(self, soup: BeautifulSoup) -> List[Document]:
        """Find direct PDF links on the page"""
        documents = []
        
        # Find all links to PDFs
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True)
            
            # Check if it's a PDF and contains meeting keywords
            if href.endswith('.pdf') or 'pdf' in href.lower():
                if any(word in text.lower() for word in ['agenda', 'minutes', 'meeting']):
                    doc_type = 'minutes' if 'minutes' in text.lower() else 'agenda'
                    
                    # Extract date
                    date_str = self._extract_date(text)
                    
                    # Make URL absolute
                    full_url = urljoin(self.meeting_url, href)
                    
                    doc = Document(
                        council_id=self.council_id,
                        council_name=self.council_name,
                        document_type=doc_type,
                        meeting_type=self._determine_meeting_type(text),
                        title=text,
                        date=date_str,
                        url=full_url,
                        webpage_url=self.meeting_url
                    )
                    documents.append(doc)
        
        return documents
    
    def _find_meeting_lists(self, soup: BeautifulSoup) -> List[Document]:
        """Find meetings in list structures"""
        documents = []
        
        # Look for UL/OL with meeting links
        for list_elem in soup.find_all(['ul', 'ol']):
            for li in list_elem.find_all('li'):
                # Check if this looks like a meeting item
                text = li.get_text(strip=True)
                if any(word in text.lower() for word in ['agenda', 'minutes', 'meeting']):
                    # Find links within this item
                    for link in li.find_all('a', href=True):
                        href = link['href']
                        link_text = link.get_text(strip=True)
                        
                        doc_type = 'minutes' if 'minutes' in link_text.lower() else 'agenda'
                        date_str = self._extract_date(text + ' ' + link_text)
                        full_url = urljoin(self.meeting_url, href)
                        
                        doc = Document(
                            council_id=self.council_id,
                            council_name=self.council_name,
                            document_type=doc_type,
                            meeting_type=self._determine_meeting_type(text),
                            title=link_text or text[:100],
                            date=date_str,
                            url=full_url,
                            webpage_url=self.meeting_url
                        )
                        documents.append(doc)
        
        return documents
    
    def _find_table_rows(self, soup: BeautifulSoup) -> List[Document]:
        """Find meetings in table structures"""
        documents = []
        
        for table in soup.find_all('table'):
            for row in table.find_all('tr'):
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    # Look for meeting info in cells
                    row_text = ' '.join(cell.get_text(strip=True) for cell in cells)
                    
                    if any(word in row_text.lower() for word in ['agenda', 'minutes']):
                        # Find links in this row
                        for link in row.find_all('a', href=True):
                            href = link['href']
                            link_text = link.get_text(strip=True)
                            
                            doc_type = 'minutes' if 'minutes' in row_text.lower() else 'agenda'
                            date_str = self._extract_date(row_text)
                            full_url = urljoin(self.meeting_url, href)
                            
                            doc = Document(
                                council_id=self.council_id,
                                council_name=self.council_name,
                                document_type=doc_type,
                                meeting_type=self._determine_meeting_type(row_text),
                                title=link_text or row_text[:100],
                                date=date_str,
                                url=full_url,
                                webpage_url=self.meeting_url
                            )
                            documents.append(doc)
        
        return documents
    
    def _find_infocouncil_pattern(self, soup: BeautifulSoup) -> List[Document]:
        """Find InfoCouncil/ePathway style meeting links"""
        documents = []
        
        # Look for common InfoCouncil patterns
        # These often have specific classes or IDs
        meeting_containers = soup.find_all('div', class_=re.compile(r'meeting|agenda|minutes', re.I))
        
        for container in meeting_containers:
            # Find all links within
            for link in container.find_all('a', href=True):
                href = link['href']
                text = link.get_text(strip=True)
                
                # Check if it looks like a meeting document
                if any(word in text.lower() for word in ['agenda', 'minutes']):
                    doc_type = 'minutes' if 'minutes' in text.lower() else 'agenda'
                    date_str = self._extract_date(text)
                    full_url = urljoin(self.meeting_url, href)
                    
                    doc = Document(
                        council_id=self.council_id,
                        council_name=self.council_name,
                        document_type=doc_type,
                        meeting_type=self._determine_meeting_type(text),
                        title=text,
                        date=date_str,
                        url=full_url,
                        webpage_url=self.meeting_url
                    )
                    documents.append(doc)
        
        return documents
    
    def _extract_date(self, text: str) -> str:
        """Extract date from text"""
        # Common date patterns
        patterns = [
            r'\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}',
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'\d{1,2}-\d{1,2}-\d{4}',
            r'\d{4}-\d{2}-\d{2}',
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group()
        
        # Try to find year at least
        year_match = re.search(r'\b(2024|2025)\b', text)
        if year_match:
            return year_match.group()
        
        return ''
    
    def _determine_meeting_type(self, text: str) -> str:
        """Determine meeting type from text"""
        text_lower = text.lower()
        
        if 'special' in text_lower:
            return 'Special Meeting'
        elif 'committee' in text_lower:
            return 'Committee Meeting'
        elif 'ordinary' in text_lower or 'regular' in text_lower:
            return 'Ordinary Meeting'
        elif 'council' in text_lower:
            return 'Council Meeting'
        else:
            return 'Meeting'


class SmartCouncilScraper(GenericCouncilScraper):
    """Enhanced scraper with more intelligent pattern detection"""
    
    def scrape(self) -> List[Document]:
        """Enhanced scraping with multiple strategies"""
        documents = []
        
        # Try main page
        documents.extend(super().scrape())
        
        # Try common subpages
        subpages = [
            'agendas-and-minutes',
            'agendas-minutes',
            'meeting-agendas',
            'council-meeting-agendas',
            'current-agendas',
            '2025',
            'meetings-2025'
        ]
        
        for subpage in subpages:
            try:
                # Try as path segment
                test_url = urljoin(self.meeting_url, subpage)
                response = requests.get(test_url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    documents.extend(self._find_pdf_links(soup))
                    documents.extend(self._find_meeting_lists(soup))
            except:
                continue
        
        # Try to find "View more" or "Archive" links
        try:
            response = requests.get(self.meeting_url, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                link_text = link.get_text(strip=True).lower()
                if any(word in link_text for word in ['more', 'archive', 'previous', 'past', 'all']):
                    archive_url = urljoin(self.meeting_url, link['href'])
                    try:
                        archive_response = requests.get(archive_url, timeout=10)
                        if archive_response.status_code == 200:
                            archive_soup = BeautifulSoup(archive_response.text, 'html.parser')
                            documents.extend(self._find_pdf_links(archive_soup))
                    except:
                        continue
        except:
            pass
        
        # Deduplicate
        seen_urls = set()
        unique_docs = []
        for doc in documents:
            if doc.url not in seen_urls:
                seen_urls.add(doc.url)
                unique_docs.append(doc)
        
        # Sort by date (most recent first)
        unique_docs.sort(key=lambda x: x.date, reverse=True)
        
        return unique_docs[:50]  # Limit to 50 most recent
