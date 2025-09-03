"""
Add Frankston City (InfoCouncil) scraper
"""

import sys
sys.path.append('src')

from scrapers.base import BaseScraper, ScraperReturn
import requests
from bs4 import BeautifulSoup

class FrankstonScraper(BaseScraper):
    """Scraper for Frankston City Council (InfoCouncil)"""
    
    def __init__(self):
        super().__init__(
            council_id="FRAN",
            council_name="Frankston City Council",
            state="VIC",
            base_url="https://frankston.infocouncil.biz"
        )
    
    def scrape(self):
        """Scrape Frankston InfoCouncil portal"""
        results = []
        
        # Try the year pattern that worked for Whitehorse
        test_urls = [
            f"{self.base_url}/Default.aspx?Year=2025",
            f"{self.base_url}/Open/2025/",
            f"{self.base_url}/"
        ]
        
        for url in test_urls:
            print(f"  Trying: {url}")
            html = self.fetch_page(url)
            
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                
                # Look for meeting links
                found = False
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    text = link.get_text(strip=True)
                    
                    # InfoCouncil patterns
                    if any(pattern in href.lower() for pattern in ['meeting.aspx', 'download.aspx', '.pdf']):
                        if any(word in text.lower() for word in ['agenda', 'minutes']):
                            # Make URL absolute
                            if not href.startswith('http'):
                                href = self.base_url + ('/' + href if not href.startswith('/') else href)
                            
                            doc_type = 'minutes' if 'minutes' in text.lower() else 'agenda'
                            date_str = self.extract_date(text)
                            
                            results.append(ScraperReturn(
                                name=text,
                                date=date_str or "",
                                time="",
                                webpage_url=url,
                                download_url=href
                            ))
                            found = True
                
                if found:
                    print(f"    Found {len(results)} documents")
                    break
        
        return results

# Test the scraper
if __name__ == "__main__":
    scraper = FrankstonScraper()
    docs = scraper.scrape()
    
    print(f"\nFrankston results: {len(docs)} documents")
    for doc in docs[:5]:
        print(f"  - {doc.name}")
        print(f"    Date: {doc.date}")
        print(f"    URL: {doc.download_url[:60]}...")
