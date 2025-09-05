"""
Fixed scrapers for Yarra and Stonnington councils
These replace the non-working scrapers with improved versions
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
from m9_adapted import MeetingDocument, BaseM9Scraper


class YarraFixedScraper(BaseM9Scraper):
    """Fixed Yarra scraper - combines web scraping with known patterns"""
    
    def __init__(self):
        super().__init__(
            council_id="YARR",
            council_name="Yarra City Council",
            base_url="https://www.yarracity.vic.gov.au"
        )
    
    def probe_url(self, url):
        """Check if a URL exists and is a PDF"""
        try:
            response = requests.head(url, headers=self.headers, timeout=3, allow_redirects=True)
            content_type = response.headers.get('Content-Type', '').lower()
            return response.status_code in (200, 206) and 'pdf' in content_type
        except:
            return False
    
    def scrape(self):
        """Scrape Yarra using multiple approaches"""
        results = []
        
        # Approach 1: Scrape the council meetings page
        meetings_url = "https://www.yarracity.vic.gov.au/about-us/council-meetings"
        
        try:
            response = requests.get(meetings_url, headers=self.headers, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all links that might be PDFs
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    # Check if it's a PDF link
                    if '.pdf' in href.lower() or 'agenda' in text.lower() or 'minutes' in text.lower():
                        # Make URL absolute
                        if not href.startswith('http'):
                            if href.startswith('/'):
                                href = self.base_url + href
                            else:
                                href = self.base_url + '/' + href
                        
                        # Determine document type
                        doc_type = None
                        if 'minutes' in href.lower() or 'minutes' in text.lower():
                            doc_type = 'minutes'
                        elif 'agenda' in href.lower() or 'agenda' in text.lower():
                            doc_type = 'agenda'
                        
                        if doc_type:
                            # Extract date
                            date_str = self.extract_date(text)
                            if not date_str:
                                # Try extracting from URL
                                date_match = re.search(r'(\d{1,2})[_-](\w+)[_-](\d{4})', href)
                                if date_match:
                                    date_str = self.extract_date(f"{date_match.group(1)} {date_match.group(2)} {date_match.group(3)}")
                            
                            if date_str:
                                doc = MeetingDocument(
                                    council_id=self.council_id,
                                    council_name=self.council_name,
                                    document_type=doc_type,
                                    meeting_type='council',
                                    title=text or f"Council Meeting {doc_type.title()} - {date_str}",
                                    date=date_str,
                                    url=href,
                                    webpage_url=meetings_url
                                )
                                results.append(doc)
        except Exception as e:
            pass  # Silently continue
        
        # Approach 2: Try known URL patterns for recent months
        current_date = datetime.now()
        
        # Check last 6 months of potential meeting dates
        for months_back in range(6):
            check_month = current_date - timedelta(days=30 * months_back)
            year = check_month.strftime('%Y')
            month = check_month.strftime('%m')
            year_month = f"{year}-{month}"
            
            # Yarra typically meets on 2nd and 4th Tuesday
            # Generate potential meeting dates
            potential_dates = []
            
            # Find all Tuesdays in the month
            first_day = datetime(check_month.year, check_month.month, 1)
            for day in range(1, 32):
                try:
                    date = datetime(check_month.year, check_month.month, day)
                    if date.weekday() == 1:  # Tuesday
                        potential_dates.append(date)
                except:
                    break
            
            # Check 2nd and 4th Tuesday (if they exist)
            for i in [1, 3]:  # 2nd and 4th elements
                if i < len(potential_dates):
                    date = potential_dates[i]
                    if date <= current_date:
                        day = date.strftime('%d')
                        date_str = date.strftime('%Y-%m-%d')
                        
                        # Try various URL patterns
                        patterns = [
                            f"/sites/default/files/{year_month}/{year}{month}{day}-council-agenda.pdf",
                            f"/sites/default/files/{year_month}/{year}{month}{day}_council_agenda.pdf",
                            f"/sites/default/files/{year_month}/{year}{month}{day}-council-minutes.pdf",
                            f"/sites/default/files/{year_month}/{year}{month}{day}_council_minutes.pdf",
                        ]
                        
                        for pattern in patterns:
                            url = self.base_url + pattern
                            if self.probe_url(url):
                                doc_type = 'minutes' if 'minutes' in pattern else 'agenda'
                                
                                doc = MeetingDocument(
                                    council_id=self.council_id,
                                    council_name=self.council_name,
                                    document_type=doc_type,
                                    meeting_type='council',
                                    title=f"Council Meeting {doc_type.title()} - {date_str}",
                                    date=date_str,
                                    url=url,
                                    webpage_url=self.base_url + "/about-us/council-meetings"
                                )
                                results.append(doc)
        
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


class StonningtonFixedScraper(BaseM9Scraper):
    """Fixed Stonnington scraper - tries both main site and InfoCouncil"""
    
    def __init__(self):
        super().__init__(
            council_id="STON",
            council_name="Stonnington City Council",
            base_url="https://www.stonnington.vic.gov.au"
        )
        self.infocouncil_base = "https://stonnington.infocouncil.biz"
    
    def probe_url(self, url):
        """Check if a URL exists and is a PDF"""
        try:
            # Use Range header to avoid downloading full files
            test_headers = dict(self.headers)
            test_headers['Range'] = 'bytes=0-0'
            response = requests.get(url, headers=test_headers, timeout=3, allow_redirects=True)
            content_type = response.headers.get('Content-Type', '').lower()
            return response.status_code in (200, 206) and 'pdf' in content_type
        except:
            return False
    
    def scrape(self):
        """Scrape Stonnington using multiple approaches"""
        results = []
        
        # Approach 1: Try the main council website patterns
        base = f"{self.base_url}/files/assets/public/v/2/about/council-meetings"
        
        current_date = datetime.now()
        
        # Check last 4 months of potential meeting dates
        for weeks_back in range(16):
            check_date = current_date - timedelta(weeks=weeks_back)
            
            # Stonnington typically meets on Tuesdays
            # Find Tuesday of that week
            days_until_tuesday = (1 - check_date.weekday()) % 7
            if days_until_tuesday == 0:
                tuesday = check_date
            else:
                tuesday = check_date + timedelta(days=days_until_tuesday)
            
            if tuesday > current_date:
                continue
            
            year = tuesday.strftime('%Y')
            dd = tuesday.strftime('%d')
            month_full = tuesday.strftime('%B').lower()
            month_short = tuesday.strftime('%b').lower()
            date_str = tuesday.strftime('%Y-%m-%d')
            
            # Try various URL patterns
            patterns = [
                (f"{base}/{year}/{dd}-{month_short}-{year}/agenda.pdf", 'agenda'),
                (f"{base}/{year}/{dd}-{month_full}-{year}/agenda.pdf", 'agenda'),
                (f"{base}/{year}/{dd}-{month_short}-{year}/minutes.pdf", 'minutes'),
                (f"{base}/{year}/{dd}-{month_full}-{year}/minutes.pdf", 'minutes'),
            ]
            
            for url, doc_type in patterns:
                if self.probe_url(url):
                    doc = MeetingDocument(
                        council_id=self.council_id,
                        council_name=self.council_name,
                        document_type=doc_type,
                        meeting_type='council',
                        title=f"Council Meeting {doc_type.title()} - {date_str}",
                        date=date_str,
                        url=url,
                        webpage_url=f"{self.base_url}/About/Council-meetings"
                    )
                    results.append(doc)
                    break  # Found a working pattern for this date
        
        # Approach 2: Try InfoCouncil pattern
        # InfoCouncil uses formats like: ORD_DDMMYYYY_AGN_AT.PDF, OCM_DDMMYYYY_MIN.PDF
        
        for weeks_back in range(16):
            check_date = current_date - timedelta(weeks=weeks_back)
            
            # Find Tuesday of that week
            days_until_tuesday = (1 - check_date.weekday()) % 7
            if days_until_tuesday == 0:
                tuesday = check_date
            else:
                tuesday = check_date + timedelta(days=days_until_tuesday)
            
            if tuesday > current_date:
                continue
            
            # Format date as DDMMYYYY
            date_code = tuesday.strftime("%d%m%Y")
            date_str = tuesday.strftime("%Y-%m-%d")
            month_year = tuesday.strftime("%Y/%m")
            
            # Try both direct and redirect URLs, with multiple prefixes
            patterns = []
            for p in ["ORD", "OCM", "CM"]:
                patterns.append((f"{self.infocouncil_base}/Open/{month_year}/{p}_{date_code}_AGN_AT.PDF", 'agenda'))
                patterns.append((f"{self.infocouncil_base}/Open/{month_year}/{p}_{date_code}_AGN.PDF", 'agenda'))
                patterns.append((f"{self.infocouncil_base}/Open/{month_year}/{p}_{date_code}_MIN.PDF", 'minutes'))
            
            for url, doc_type in patterns:
                if self.probe_url(url):
                    doc = MeetingDocument(
                        council_id=self.council_id,
                        council_name=self.council_name,
                        document_type=doc_type,
                        meeting_type='council',
                        title=f"Council Meeting {doc_type.title()} - {date_str}",
                        date=date_str,
                        url=url,
                        webpage_url=self.infocouncil_base
                    )
                    results.append(doc)

        # Month discovery fallback
        if not results:
            try:
                from src.utils.infocouncil import discover_month_files, parse_infocouncil_filename
                for i in range(0, 6):
                    dt = current_date - timedelta(days=30*i)
                    files = discover_month_files(self.infocouncil_base, dt.year, dt.month, self.session, self.headers)
                    for u in files:
                        kind, iso = parse_infocouncil_filename(u)
                        if not kind or not iso:
                            continue
                        results.append(MeetingDocument(
                            council_id=self.council_id,
                            council_name=self.council_name,
                            document_type=kind,
                            meeting_type='council',
                            title=f"Council Meeting {kind.title()} - {iso}",
                            date=iso,
                            url=u,
                            webpage_url=self.infocouncil_base
                        ))
            except Exception:
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
