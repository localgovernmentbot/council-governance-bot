"""
Port Phillip InfoCouncil scraper using discovered pattern
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
from dateutil.parser import parse as parse_date
from m9_adapted import MeetingDocument, BaseM9Scraper


class PortPhillipInfoCouncilScraper(BaseM9Scraper):
    """Port Phillip scraper using InfoCouncil pattern"""
    
    def __init__(self):
        super().__init__(
            council_id="PORT",
            council_name="Port Phillip City Council",
            base_url="https://portphillip.infocouncil.biz"
        )
    
    def scrape(self):
        """Scrape Port Phillip InfoCouncil"""
        results = []
        
        # Check recent months
        current_date = datetime.now()
        
        for months_back in range(6):  # Last 6 months
            check_date = current_date - timedelta(days=30 * months_back)
            year = check_date.strftime("%Y")
            month = check_date.strftime("%m")
            
            # Try the Open directory for this month
            month_url = f"{self.base_url}/Open/{year}/{month}/"
            
            try:
                response = requests.get(month_url, headers=self.headers, timeout=30)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find all links in this month's directory
                    for link in soup.find_all('a', href=True):
                        href = link.get('href', '')
                        text = link.get_text(strip=True)
                        
                        # Check for meeting files
                        if 'ORD_' in href or 'RedirectToDoc.aspx' in href:
                            # Extract date from filename
                            date_match = re.search(r'ORD_(\d{8})', href)
                            if date_match:
                                date_str = date_match.group(1)
                                # Convert DDMMYYYY to YYYY-MM-DD
                                try:
                                    parsed_date = datetime.strptime(date_str, "%d%m%Y")
                                    formatted_date = parsed_date.strftime("%Y-%m-%d")
                                except:
                                    continue
                                
                                # Determine document type
                                if '_MIN' in href:
                                    doc_type = 'minutes'
                                elif '_AGN' in href:
                                    doc_type = 'agenda'
                                else:
                                    continue
                                
                                # Create URL
                                if 'RedirectToDoc.aspx' in href:
                                    full_url = self.base_url + '/' + href if not href.startswith('/') else self.base_url + href
                                else:
                                    # Convert HTML link to PDF
                                    pdf_path = href.replace('_WEB.htm', '.PDF').replace('.htm', '.PDF')
                                    full_url = f"{self.base_url}/RedirectToDoc.aspx?URL={pdf_path}"
                                
                                doc = MeetingDocument(
                                    council_id=self.council_id,
                                    council_name=self.council_name,
                                    document_type=doc_type,
                                    meeting_type='ordinary',
                                    title=f"Ordinary Council Meeting {doc_type.title()} - {formatted_date}",
                                    date=formatted_date,
                                    url=full_url,
                                    webpage_url=month_url
                                )
                                results.append(doc)
                
            except Exception as e:
                pass
        
        # Also check the main page
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for recent meeting links
                for link in soup.find_all('a', href=lambda x: x and ('ORD_' in x or 'meeting' in x.lower())):
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    # Extract date
                    date_str = self.extract_date(text)
                    if not date_str:
                        date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})', text)
                        if date_match:
                            date_str = self.extract_date(date_match.group())
                    
                    if date_str and '.pdf' in href.lower():
                        doc_type = self.determine_doc_type(text) or 'agenda'
                        
                        if not href.startswith('http'):
                            href = self.base_url + '/' + href.lstrip('/')
                        
                        doc = MeetingDocument(
                            council_id=self.council_id,
                            council_name=self.council_name,
                            document_type=doc_type,
                            meeting_type='council',
                            title=text,
                            date=date_str,
                            url=href,
                            webpage_url=self.base_url
                        )
                        results.append(doc)
                        
        except:
            pass
        
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
    print("Testing Port Phillip InfoCouncil Scraper")
    print("=" * 50)
    
    scraper = PortPhillipInfoCouncilScraper()
    docs = scraper.scrape()
    
    print(f"\nFound {len(docs)} documents")
    
    # Show first few
    for doc in docs[:5]:
        print(f"\n{doc.date} - {doc.document_type}")
        print(f"  URL: {doc.url}")
