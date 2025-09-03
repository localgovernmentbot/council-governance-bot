"""
Final working scraper for Port Phillip using InfoCouncil
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
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
        """Scrape Port Phillip from InfoCouncil"""
        results = []
        
        # Try current and previous months
        current_date = datetime.now()
        
        for months_back in range(6):  # Last 6 months
            check_date = current_date - timedelta(days=30 * months_back)
            year = check_date.strftime("%Y")
            month = check_date.strftime("%m")
            
            # InfoCouncil directory pattern
            url = f"{self.base_url}/Open/{year}/{month}/"
            
            try:
                response = requests.get(url, headers=self.headers, timeout=30)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find all links in the directory
                    for link in soup.find_all('a', href=True):
                        href = link.get('href', '')
                        text = link.get_text(strip=True)
                        
                        # Look for PDF files
                        if '.PDF' in href.upper():
                            # Extract date from filename
                            # Pattern: ORD_02092025_AGN_AT.PDF
                            date_match = re.search(r'_(\d{8})_', href)
                            if date_match:
                                date_digits = date_match.group(1)
                                # Convert DDMMYYYY to date
                                try:
                                    parsed_date = datetime.strptime(date_digits, "%d%m%Y")
                                    date_str = parsed_date.strftime("%Y-%m-%d")
                                except:
                                    continue
                            else:
                                # Try extracting from text
                                date_str = self.extract_date(text)
                                if not date_str:
                                    continue
                            
                            # Determine document type
                            if 'AGN' in href.upper() or 'agenda' in text.lower():
                                doc_type = 'agenda'
                            elif 'MIN' in href.upper() or 'minutes' in text.lower():
                                doc_type = 'minutes'
                            else:
                                doc_type = 'agenda'  # Default
                            
                            # Determine meeting type
                            if 'ORD' in href.upper():
                                meeting_type = 'ordinary'
                            else:
                                meeting_type = 'council'
                            
                            # Make URL absolute
                            if not href.startswith('http'):
                                if href.startswith('/'):
                                    href = self.base_url + href
                                else:
                                    href = url + href
                            
                            doc = MeetingDocument(
                                council_id=self.council_id,
                                council_name=self.council_name,
                                document_type=doc_type,
                                meeting_type=meeting_type,
                                title=text or f"{meeting_type.title()} Council Meeting {doc_type.title()} - {date_str}",
                                date=date_str,
                                url=href,
                                webpage_url=url
                            )
                            results.append(doc)
                    
                    print(f"  Found {len([d for d in results if f'{year}-{month}' in d.date])} documents for {year}/{month}")
                    
            except Exception as e:
                pass
        
        # Also try the base URL
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for recent meeting links
                for link in soup.find_all('a', href=lambda x: x and 'Open/' in x):
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    if '.PDF' in href.upper():
                        date_str = self.extract_date(text)
                        if date_str:
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
        
        # Remove duplicates and sort
        seen_urls = set()
        unique_results = []
        for doc in results:
            if doc.url not in seen_urls:
                seen_urls.add(doc.url)
                unique_results.append(doc)
        
        unique_results.sort(key=lambda x: x.date, reverse=True)
        return unique_results


# Test all three final scrapers
if __name__ == "__main__":
    print("FINAL TEST: All 3 Remaining Councils")
    print("=" * 60)
    
    # Import the other scrapers
    from m9_final_three import YarraFinalScraper, StonningtonFinalScraper
    
    scrapers = [
        ("Yarra", YarraFinalScraper),
        ("Stonnington", StonningtonFinalScraper),
        ("Port Phillip", PortPhillipInfoCouncilScraper),
    ]
    
    total = 0
    working = 0
    
    for name, scraper_class in scrapers:
        print(f"\n{name}:")
        try:
            scraper = scraper_class()
            docs = scraper.scrape()
            print(f"  ✓ Found {len(docs)} documents")
            
            if docs:
                working += 1
                for doc in docs[:3]:
                    print(f"    - {doc.date}: {doc.title[:50]}...")
            
            total += len(docs)
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print(f"\n{'='*60}")
    print(f"Working: {working}/3 councils")
    print(f"Total new documents: {total}")
    
    if working == 3:
        print("\n🎉 SUCCESS! All 9 M9 councils now have working scrapers!")
        print(f"Expected total documents: {318 + total} from all 9 councils")
