#!/usr/bin/env python3
"""
Yarra scraper using discovered PDF pattern
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
from m9_adapted import MeetingDocument, BaseM9Scraper

class YarraWorkingScraper(BaseM9Scraper):
    """Yarra scraper that actually finds documents"""
    
    def __init__(self):
        super().__init__(
            council_id="YARR",
            council_name="Yarra City Council",
            base_url="https://www.yarracity.vic.gov.au"
        )
    
    def scrape(self):
        """Scrape Yarra by finding meeting pages and extracting PDFs"""
        results = []
        
        # First, get the list of council meetings
        list_url = "https://www.yarracity.vic.gov.au/about-us/committees-meetings-and-minutes"
        
        try:
            response = requests.get(list_url, headers=self.headers, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all links to council meeting pages
                meeting_urls = []
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    # Pattern: /about-us/committees-meetings-and-minutes/council-meeting-DATE
                    if '/council-meeting-' in href and not href.endswith('.pdf'):
                        full_url = href if href.startswith('http') else self.base_url + href
                        meeting_urls.append(full_url)
                
                print(f"  Found {len(meeting_urls)} meeting pages")
                
                # Visit each meeting page
                for meeting_url in meeting_urls[:20]:  # Limit to recent 20
                    try:
                        meeting_response = requests.get(meeting_url, headers=self.headers, timeout=30)
                        if meeting_response.status_code == 200:
                            meeting_soup = BeautifulSoup(meeting_response.text, 'html.parser')
                            
                            # Extract date from URL or page
                            date_match = re.search(r'(\d{1,2}-\w+-\d{4})', meeting_url)
                            if date_match:
                                date_str = self.extract_date(date_match.group())
                            else:
                                # Try to find date on page
                                date_elem = meeting_soup.find("strong", string="Date and time:")
                                if date_elem:
                                    parent = date_elem.find_parent("p")
                                    if parent:
                                        date_str = self.extract_date(parent.get_text())
                                else:
                                    continue
                            
                            if not date_str:
                                continue
                            
                            # Find download links
                            for link in meeting_soup.find_all('a', href=True):
                                href = link.get('href', '')
                                text = link.get_text(strip=True)
                                
                                # Check if it's a PDF link
                                if '.pdf' in href.lower():
                                    # Determine document type
                                    doc_type = self.determine_doc_type(text)
                                    if not doc_type:
                                        if 'minutes' in href.lower() or 'minutes' in text.lower():
                                            doc_type = 'minutes'
                                        elif 'agenda' in href.lower() or 'agenda' in text.lower():
                                            doc_type = 'agenda'
                                        else:
                                            continue
                                    
                                    # Make URL absolute
                                    if not href.startswith('http'):
                                        href = self.base_url + href
                                    
                                    doc = MeetingDocument(
                                        council_id=self.council_id,
                                        council_name=self.council_name,
                                        document_type=doc_type,
                                        meeting_type='council',
                                        title=text or f"Council Meeting {doc_type.title()} - {date_str}",
                                        date=date_str,
                                        url=href,
                                        webpage_url=meeting_url
                                    )
                                    results.append(doc)
                    
                    except Exception as e:
                        pass
                
                # Also try direct PDF search on main page
                for link in soup.find_all('a', href=lambda x: x and '.pdf' in x.lower()):
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    if any(word in text.lower() for word in ['agenda', 'minutes']):
                        date_str = self.extract_date(text)
                        if date_str:
                            doc_type = self.determine_doc_type(text)
                            
                            if not href.startswith('http'):
                                href = self.base_url + href
                            
                            doc = MeetingDocument(
                                council_id=self.council_id,
                                council_name=self.council_name,
                                document_type=doc_type or 'agenda',
                                meeting_type='council',
                                title=text,
                                date=date_str,
                                url=href,
                                webpage_url=list_url
                            )
                            results.append(doc)
                            
        except Exception as e:
            print(f"  Error: {e}")
        
        # Remove duplicates
        seen_urls = set()
        unique_results = []
        for doc in results:
            if doc.url not in seen_urls:
                seen_urls.add(doc.url)
                unique_results.append(doc)
        
        # Sort by date
        unique_results.sort(key=lambda x: x.date, reverse=True)
        
        return unique_results

# Test it
if __name__ == "__main__":
    print("Testing Yarra Working Scraper")
    print("=" * 40)
    
    scraper = YarraWorkingScraper()
    docs = scraper.scrape()
    
    print(f"\nFound {len(docs)} documents")
    
    # Show first few
    for doc in docs[:5]:
        print(f"\n{doc.date} - {doc.document_type}")
        print(f"  Title: {doc.title}")
        print(f"  URL: {doc.url}")
