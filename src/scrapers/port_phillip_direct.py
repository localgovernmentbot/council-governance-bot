"""
Port Phillip scraper using direct URL generation
"""

import requests
from datetime import datetime, timedelta
from m9_adapted import MeetingDocument, BaseM9Scraper


class PortPhillipDirectScraper(BaseM9Scraper):
    """Port Phillip scraper that generates URLs directly"""
    
    def __init__(self):
        super().__init__(
            council_id="PORT",
            council_name="Port Phillip City Council",
            base_url="https://portphillip.infocouncil.biz"
        )
    
    def scrape(self):
        """Generate Port Phillip URLs based on pattern"""
        results = []
        
        # Port Phillip meetings are typically on Tuesdays
        # Pattern: ORD_DDMMYYYY_AGN_AT.PDF for agenda
        # Pattern: ORD_DDMMYYYY_MIN.PDF for minutes
        
        # Check last 6 months of Tuesdays
        current_date = datetime.now()
        
        for weeks_back in range(26):  # ~6 months
            check_date = current_date - timedelta(weeks=weeks_back)
            
            # Find the Tuesday of that week
            days_ahead = 1 - check_date.weekday()  # Tuesday is 1
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            tuesday = check_date + timedelta(days=days_ahead)
            
            # Format date as DDMMYYYY
            date_str = tuesday.strftime("%d%m%Y")
            formatted_date = tuesday.strftime("%Y-%m-%d")
            month_year = tuesday.strftime("%Y/%m")
            
            # Generate URLs for agenda and minutes
            agenda_url = f"{self.base_url}/RedirectToDoc.aspx?URL=Open/{month_year}/ORD_{date_str}_AGN_AT.PDF"
            minutes_url = f"{self.base_url}/RedirectToDoc.aspx?URL=Open/{month_year}/ORD_{date_str}_MIN.PDF"
            
            # Test if documents exist
            for doc_type, url in [('agenda', agenda_url), ('minutes', minutes_url)]:
                try:
                    # Just check headers to see if document exists
                    response = requests.head(url, headers=self.headers, timeout=10, allow_redirects=True)
                    
                    # Check if it's a PDF (not an error page)
                    content_type = response.headers.get('Content-Type', '')
                    if response.status_code == 200 and 'pdf' in content_type.lower():
                        doc = MeetingDocument(
                            council_id=self.council_id,
                            council_name=self.council_name,
                            document_type=doc_type,
                            meeting_type='ordinary',
                            title=f"Ordinary Council Meeting {doc_type.title()} - {formatted_date}",
                            date=formatted_date,
                            url=url,
                            webpage_url=self.base_url
                        )
                        results.append(doc)
                        print(f"  Found: {formatted_date} - {doc_type}")
                except:
                    pass
        
        # Sort by date
        results.sort(key=lambda x: x.date, reverse=True)
        
        return results


# Test it
if __name__ == "__main__":
    print("Testing Port Phillip Direct URL Scraper")
    print("=" * 50)
    print("Checking Tuesday meetings for last 6 months...\n")
    
    scraper = PortPhillipDirectScraper()
    docs = scraper.scrape()
    
    print(f"\nTotal found: {len(docs)} documents")
    
    # Count by type
    agendas = [d for d in docs if d.document_type == 'agenda']
    minutes = [d for d in docs if d.document_type == 'minutes']
    
    print(f"Agendas: {len(agendas)}")
    print(f"Minutes: {len(minutes)}")
    
    # Show recent documents
    if docs:
        print("\nRecent documents:")
        for doc in docs[:5]:
            print(f"  {doc.date} - {doc.document_type}: {doc.url}")
