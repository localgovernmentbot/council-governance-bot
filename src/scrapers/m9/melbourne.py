"""
Melbourne City Council Scraper for M9 Bot
Adapted from our working scraper
"""

from ..base_m9 import BaseM9Scraper, MeetingDocument
from bs4 import BeautifulSoup
import re


class MelbourneScraper(BaseM9Scraper):
    """Scraper for City of Melbourne"""
    
    def __init__(self):
        super().__init__(
            council_id="MELB",
            council_name="City of Melbourne"
        )
    
    def scrape(self):
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
