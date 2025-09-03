"""
Add remaining M9 scrapers - Moonee Valley, Port Phillip, Stonnington, Yarra
"""

from bs4 import BeautifulSoup
import re
from datetime import datetime
from dateutil.parser import parse as parse_date
from dataclasses import dataclass
from typing import Optional, List
import requests

# Import base classes
from m9_adapted import BaseM9Scraper, MeetingDocument


class MooneeValleyScraper(BaseM9Scraper):
    """Moonee Valley scraper adapted from YIMBY (uses table structure)"""
    
    def __init__(self):
        super().__init__(
            council_id="MOON",
            council_name="Moonee Valley City Council",
            base_url="https://mvcc.vic.gov.au"
        )
    
    def scrape(self):
        """Scrape all Moonee Valley meeting documents"""
        results = []
        
        url = "https://mvcc.vic.gov.au/my-council/council-meetings/"
        html = self.fetch_page(url)
        
        if not html:
            return results
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find the meetings table
        tables = soup.find_all("table")
        if not tables:
            return results
            
        # First table should contain meetings
        table = tables[0].find("tbody")
        if not table:
            return results
        
        # Process each row
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) < 3:
                continue
            
            # Column 1: Date/time
            datetime_text = cells[0].text.strip()
            date_str = self.extract_date(datetime_text)
            if not date_str:
                continue
            
            # Column 2: Agenda link
            agenda_cell = cells[1]
            agenda_link = agenda_cell.find("a")
            if agenda_link and agenda_link.get("href"):
                agenda_url = agenda_link["href"]
                if not agenda_url.startswith('http'):
                    agenda_url = self.base_url + agenda_url
                
                doc = MeetingDocument(
                    council_id=self.council_id,
                    council_name=self.council_name,
                    document_type='agenda',
                    meeting_type='council',
                    title=f"Council Meeting Agenda - {date_str}",
                    date=date_str,
                    url=agenda_url,
                    webpage_url=url
                )
                results.append(doc)
            
            # Column 3: Minutes link (if available)
            if len(cells) > 2:
                minutes_cell = cells[2]
                minutes_link = minutes_cell.find("a")
                if minutes_link and minutes_link.get("href"):
                    minutes_url = minutes_link["href"]
                    if not minutes_url.startswith('http'):
                        minutes_url = self.base_url + minutes_url
                    
                    doc = MeetingDocument(
                        council_id=self.council_id,
                        council_name=self.council_name,
                        document_type='minutes',
                        meeting_type='council',
                        title=f"Council Meeting Minutes - {date_str}",
                        date=date_str,
                        url=minutes_url,
                        webpage_url=url
                    )
                    results.append(doc)
        
        # Sort by date (newest first)
        results.sort(key=lambda x: x.date, reverse=True)
        
        return results


class YarraScraper(BaseM9Scraper):
    """Yarra scraper adapted from YIMBY"""
    
    def __init__(self):
        super().__init__(
            council_id="YARR",
            council_name="Yarra City Council",
            base_url="https://www.yarracity.vic.gov.au"
        )
    
    def scrape(self):
        """Scrape all Yarra meeting documents"""
        results = []
        
        # Try both upcoming and past meetings
        urls = [
            "https://www.yarracity.vic.gov.au/about-us/council-and-committee-meetings/upcoming-council-and-committee-meetings",
            "https://www.yarracity.vic.gov.au/about-us/council-and-committee-meetings"
        ]
        
        for url in urls:
            html = self.fetch_page(url)
            if not html:
                continue
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find meeting sections
            meeting_sections = soup.find_all("div", class_="show-for-medium-up")
            
            for section in meeting_sections:
                # Find all links in the section
                for link in section.find_all("a", href=True):
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    # Check if it's a document link
                    if any(word in text.lower() for word in ['agenda', 'minutes']):
                        # Determine document type
                        doc_type = self.determine_doc_type(text)
                        if not doc_type:
                            continue
                        
                        # Extract date
                        date_str = self.extract_date(text)
                        if not date_str:
                            # Try parent element
                            parent = link.parent
                            while parent and not date_str:
                                parent_text = parent.get_text(strip=True)
                                date_str = self.extract_date(parent_text)
                                parent = parent.parent
                        
                        if not date_str:
                            continue
                        
                        # Make URL absolute
                        if not href.startswith('http'):
                            href = self.base_url + href
                        
                        # Determine meeting type
                        meeting_type = self.determine_meeting_type(text)
                        
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
        
        # Remove duplicates (same URL)
        seen_urls = set()
        unique_results = []
        for doc in results:
            if doc.url not in seen_urls:
                seen_urls.add(doc.url)
                unique_results.append(doc)
        
        # Sort by date (newest first)
        unique_results.sort(key=lambda x: x.date, reverse=True)
        
        return unique_results


class PortPhillipScraper(BaseM9Scraper):
    """Port Phillip scraper"""
    
    def __init__(self):
        super().__init__(
            council_id="PORT",
            council_name="Port Phillip City Council",
            base_url="https://www.portphillip.vic.gov.au"
        )
    
    def scrape(self):
        """Scrape Port Phillip meeting documents"""
        results = []
        
        # Port Phillip meetings page
        url = "https://www.portphillip.vic.gov.au/about-the-council/meetings-and-minutes"
        html = self.fetch_page(url)
        
        if not html:
            return results
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for PDF links
        for link in soup.find_all('a', href=lambda x: x and '.pdf' in x.lower()):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Check if it's a meeting document
            doc_type = self.determine_doc_type(text)
            if not doc_type:
                continue
            
            # Extract date
            date_str = self.extract_date(text)
            if not date_str:
                continue
            
            # Make URL absolute
            if not href.startswith('http'):
                href = self.base_url + href
            
            # Determine meeting type
            meeting_type = self.determine_meeting_type(text)
            
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


class StonningtonScraper(BaseM9Scraper):
    """Stonnington scraper (uses InfoCouncil)"""
    
    def __init__(self):
        super().__init__(
            council_id="STON",
            council_name="Stonnington City Council",
            base_url="https://stonnington.infocouncil.biz"
        )
    
    def scrape(self):
        """Scrape Stonnington meeting documents"""
        results = []
        
        # Stonnington uses InfoCouncil - try year pattern
        year = datetime.now().year
        url = f"{self.base_url}/Open/{year}/"
        
        html = self.fetch_page(url)
        if not html:
            # Try without year
            url = self.base_url
            html = self.fetch_page(url)
        
        if not html:
            return results
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for meeting links (InfoCouncil pattern)
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # InfoCouncil patterns
            if any(pattern in href.lower() for pattern in ['meeting.aspx', 'download.aspx', '.pdf']):
                if any(word in text.lower() for word in ['agenda', 'minutes']):
                    # Determine document type
                    doc_type = self.determine_doc_type(text)
                    if not doc_type:
                        continue
                    
                    # Extract date
                    date_str = self.extract_date(text)
                    if not date_str:
                        continue
                    
                    # Make URL absolute
                    if not href.startswith('http'):
                        href = self.base_url + ('/' + href if not href.startswith('/') else href)
                    
                    # Determine meeting type
                    meeting_type = self.determine_meeting_type(text)
                    
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
