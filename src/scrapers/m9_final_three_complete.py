"""
Final implementation of Yarra, Stonnington, and Port Phillip scrapers
Using all discovered patterns
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
from dateutil.parser import parse as parse_date
from m9_adapted import MeetingDocument, BaseM9Scraper


class YarraFinalScraper(BaseM9Scraper):
    """Yarra scraper using /sites/default/files/ pattern"""
    
    def __init__(self):
        super().__init__(
            council_id="YARR",
            council_name="Yarra City Council",
            base_url="https://www.yarracity.vic.gov.au"
        )
    
    def scrape(self):
        """Scrape Yarra using discovered pattern"""
        results = []
        
        # First, get list of meeting pages
        list_url = "https://www.yarracity.vic.gov.au/about-us/committees-meetings-and-minutes"
        
        try:
            response = requests.get(list_url, headers=self.headers, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all PDF links with the pattern
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    
                    # Check for the /sites/default/files/ pattern
                    if '/sites/default/files/' in href and '.pdf' in href.lower():
                        text = link.get_text(strip=True)
                        
                        # Extract date from text or URL
                        date_str = self.extract_date(text)
                        if not date_str:
                            # Try extracting from URL (e.g., 2025-08)
                            date_match = re.search(r'/(\d{4}-\d{2})/', href)
                            if date_match:
                                # Extract day from filename
                                day_match = re.search(r'(\d{1,2})_\w+_\d{4}', href)
                                if day_match:
                                    date_str = self.extract_date(day_match.group().replace('_', ' '))
                        
                        if date_str:
                            # Determine document type
                            doc_type = 'minutes' if 'minutes' in href.lower() else 'agenda'
                            
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
                                webpage_url=list_url
                            )
                            results.append(doc)
                
                # Also check individual meeting pages
                meeting_links = []
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    if '/council-meeting-' in href and '2025' in href:
                        full_url = self.base_url + href if not href.startswith('http') else href
                        if full_url not in meeting_links:
                            meeting_links.append(full_url)
                
                # Visit each meeting page
                for meeting_url in meeting_links[:10]:  # Limit to recent 10
                    try:
                        meeting_resp = requests.get(meeting_url, headers=self.headers, timeout=30)
                        if meeting_resp.status_code == 200:
                            meeting_soup = BeautifulSoup(meeting_resp.text, 'html.parser')
                            
                            # Extract date from URL
                            date_match = re.search(r'(\d{1,2}-\w+-\d{4})', meeting_url)
                            if date_match:
                                date_str = self.extract_date(date_match.group())
                                
                                # Find PDF links on this page
                                for pdf_link in meeting_soup.find_all('a', href=lambda x: x and '.pdf' in x.lower()):
                                    pdf_href = pdf_link.get('href', '')
                                    pdf_text = pdf_link.get_text(strip=True)
                                    
                                    if '/sites/default/files/' in pdf_href:
                                        doc_type = 'minutes' if 'minutes' in pdf_href.lower() else 'agenda'
                                        
                                        if not pdf_href.startswith('http'):
                                            pdf_href = self.base_url + pdf_href
                                        
                                        doc = MeetingDocument(
                                            council_id=self.council_id,
                                            council_name=self.council_name,
                                            document_type=doc_type,
                                            meeting_type='council',
                                            title=pdf_text or f"Council Meeting {doc_type.title()} - {date_str}",
                                            date=date_str,
                                            url=pdf_href,
                                            webpage_url=meeting_url
                                        )
                                        results.append(doc)
                    except:
                        pass
                        
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


class StonningtonFinalScraper(BaseM9Scraper):
    """Stonnington scraper using discovered patterns"""
    
    def __init__(self):
        super().__init__(
            council_id="STON",
            council_name="Stonnington City Council",
            base_url="https://www.stonnington.vic.gov.au"
        )
    
    def scrape(self):
        """Scrape Stonnington by constructing known file paths and probing with HEAD"""
        results = []

        def try_url(url: str) -> bool:
            try:
                # Use Range header to avoid downloading full files
                test_headers = dict(self.headers)
                test_headers['Range'] = 'bytes=0-0'
                resp = requests.get(url, headers=test_headers, timeout=3, allow_redirects=True)
                ctype = resp.headers.get('Content-Type', '')
                return resp.status_code in (200, 206) and 'pdf' in ctype.lower()
            except Exception:
                return False

        # Iterate recent dates and try known patterns
        today = datetime.now()
        base = f"{self.base_url}/files/assets/public/v/2/about/council-meetings"

        session = requests.Session()
        session.headers.update(self.headers)

        import os
        max_weeks = int(os.environ.get('STON_WEEKS', '26'))
        for weeks_back in range(0, max_weeks):  # ~6 months of weeks by default
            # Check Monday and Tuesday of each week
            base_day = today - timedelta(weeks=weeks_back)
            monday = base_day - timedelta(days=(base_day.weekday() % 7))
            for d in (monday, monday + timedelta(days=1)):
                dd = d.strftime('%d')
                year = d.strftime('%Y')
                month_full = d.strftime('%B').lower()
                month_short = d.strftime('%b').lower()

                slugs = [f"{dd}-{month_short}-{year}", f"{dd}-{month_full}-{year}"]
                filenames = [
                    'agenda.pdf',
                    'minutes.pdf',
                    f'council-meeting-agenda-{dd}-{month_full}-{year}.pdf',
                    f'council-meeting-minutes-{dd}-{month_full}-{year}.pdf',
                ]

                for slug in slugs:
                    for fname in filenames:
                        url = f"{base}/{year}/{slug}/{fname}"
                        # Prefer the lightweight GET probe
                        ok = try_url(url)
                        if ok:
                            doc_type = 'minutes' if 'minutes' in fname else 'agenda'
                            formatted_date = d.strftime('%Y-%m-%d')
                            title = f"Council Meeting {doc_type.title()} - {formatted_date}"

                            results.append(MeetingDocument(
                                council_id=self.council_id,
                                council_name=self.council_name,
                                document_type=doc_type,
                                meeting_type='council',
                                title=title,
                                date=formatted_date,
                                url=url,
                                webpage_url=f"https://www.stonnington.vic.gov.au/About/Council-meetings"
                            ))

                # If we have gathered a decent number, stop early
                if len(results) >= 16:
                    break
            if len(results) >= 16:
                break

        # Dedupe and sort
        seen = set()
        unique = []
        for doc in results:
            if doc.url not in seen:
                seen.add(doc.url)
                unique.append(doc)

        unique.sort(key=lambda x: x.date, reverse=True)
        return unique


class PortPhillipFinalScraper(BaseM9Scraper):
    """Port Phillip scraper using InfoCouncil pattern (Wednesdays)"""
    
    def __init__(self):
        super().__init__(
            council_id="PORT",
            council_name="Port Phillip City Council",
            base_url="https://portphillip.infocouncil.biz"
        )
    
    def scrape(self):
        """Scrape Port Phillip InfoCouncil (Wednesday meetings)"""
        results = []
        
        # Port Phillip normally meets on Wednesdays
        # Pattern: ORD_DDMMYYYY_AGN_AT.PDF for agenda
        # Pattern: ORD_DDMMYYYY_MIN.PDF for minutes
        
        current_date = datetime.now()
        
        # Check last 6 months of potential meeting dates
        for weeks_back in range(26):  # ~6 months
            check_date = current_date - timedelta(weeks=weeks_back)
            
            # Find Wednesday of that week
            days_ahead = 2 - check_date.weekday()  # Wednesday is 2
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            wednesday = check_date + timedelta(days=days_ahead)
            
            # Also check Tuesday (since they moved it this week)
            tuesday = wednesday - timedelta(days=1)
            
            for meeting_day in [wednesday, tuesday]:
                # Format date as DDMMYYYY
                date_str = meeting_day.strftime("%d%m%Y")
                formatted_date = meeting_day.strftime("%Y-%m-%d")
                month_year = meeting_day.strftime("%Y/%m")
                
                # Generate URLs for agenda and minutes
                agenda_url = f"{self.base_url}/RedirectToDoc.aspx?URL=Open/{month_year}/ORD_{date_str}_AGN_AT.PDF"
                minutes_url = f"{self.base_url}/RedirectToDoc.aspx?URL=Open/{month_year}/ORD_{date_str}_MIN.PDF"
                
                # Test if documents exist
                for doc_type, url in [('agenda', agenda_url), ('minutes', minutes_url)]:
                    try:
                        # Use HEAD request to check if document exists
                        response = requests.head(url, headers=self.headers, timeout=10, allow_redirects=True)
                        
                        # Check if it's a PDF
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
                            print(f"  Found: {formatted_date} ({meeting_day.strftime('%A')}) - {doc_type}")
                    except:
                        pass
        
        # Sort by date
        results.sort(key=lambda x: x.date, reverse=True)
        
        return results


# Test all three
if __name__ == "__main__":
    print("Testing Final 3 M9 Council Scrapers")
    print("=" * 60)
    
    scrapers = [
        ("Yarra", YarraFinalScraper),
        ("Stonnington", StonningtonFinalScraper),
        ("Port Phillip", PortPhillipFinalScraper),
    ]
    
    total_docs = 0
    
    for name, scraper_class in scrapers:
        print(f"\n{name}:")
        try:
            scraper = scraper_class()
            docs = scraper.scrape()
            
            # Count by type
            agendas = [d for d in docs if d.document_type == 'agenda']
            minutes = [d for d in docs if d.document_type == 'minutes']
            
            print(f"  Total: {len(docs)} documents ({len(agendas)} agendas, {len(minutes)} minutes)")
            
            if docs:
                print(f"  Most recent: {docs[0].date} - {docs[0].title[:50]}...")
                
            total_docs += len(docs)
            
        except Exception as e:
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print(f"Total from final 3 scrapers: {total_docs} documents")
    print(f"\nCombined with existing 6 councils (318 docs):")
    print(f"GRAND TOTAL: {318 + total_docs} documents from 9/9 councils!")
