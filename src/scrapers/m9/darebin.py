"""
Darebin City Council Scraper for M9 Bot
Adapted from our working scraper
"""

from ..base_m9 import BaseM9Scraper, MeetingDocument
from bs4 import BeautifulSoup


class DarebinScraper(BaseM9Scraper):
    """Scraper for Darebin City Council"""
    
    def __init__(self):
        super().__init__(
            council_id="DARE",
            council_name="Darebin City Council"
        )
        # Override with the specific 2025 page that works
        self.meetings_url = "https://www.darebin.vic.gov.au/About-council/Council-structure-and-performance/Council-and-Committee-Meetings/Council-meetings/Meeting-agendas-and-minutes/2025-Council-meeting-agendas-and-minutes"
    
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
