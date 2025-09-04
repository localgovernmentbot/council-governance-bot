#!/usr/bin/env python3
"""
Fixed scrapers for Yarra and Stonnington councils
Combining web scraping with direct URL pattern probing
"""

import requests
import cloudscraper
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
from dateutil.parser import parse as parse_date
import sys
import os

# Add the scrapers path
sys.path.append('src/scrapers')
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
            # Prefer a Range GET via a session to avoid full download and HEAD blocks
            if not getattr(self, 'session', None):
                self.session = cloudscraper.create_scraper()
                self.session.headers.update(self.headers)
            test_headers = dict(self.headers)
            test_headers['Range'] = 'bytes=0-0'
            r = self.session.get(url, headers=test_headers, timeout=8, allow_redirects=True)
            ctype = r.headers.get('Content-Type', '').lower()
            return r.status_code in (200, 206) and ('pdf' in ctype or url.lower().endswith('.pdf'))
        except:
            return False
    
    def scrape(self):
        """Scrape Yarra using multiple approaches"""
        results = []
        
        # Approach 1: Scrape the council meetings page
        print("  Scraping Yarra council meetings page...")
        meetings_url = "https://www.yarracity.vic.gov.au/about-us/council-meetings"
        
        try:
            html = self.fetch_page(meetings_url)
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                
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
            print(f"  Error scraping meetings page: {e}")
        
        # Approach 2: Try known URL patterns for recent months
        print("  Trying known Yarra URL patterns...")
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
            for date in potential_dates[1:4:2]:  # 2nd and 4th elements (indices 1 and 3)
                if date <= current_date:
                    day = date.strftime('%d')
                    date_str = date.strftime('%Y-%m-%d')
                    
                    # Try various URL patterns
                    patterns = [
                        f"/sites/default/files/{year_month}/{year}{month}{day}-council-agenda.pdf",
                        f"/sites/default/files/{year_month}/{year}{month}{day}_council_agenda.pdf",
                        f"/sites/default/files/{year_month}/{year}{month}{day}-council-meeting-agenda.pdf",
                        f"/sites/default/files/{year_month}/{year}{month}{day}_council_meeting_agenda.pdf",
                        f"/sites/default/files/{year_month}/{year}{month}{day}-council-minutes.pdf",
                        f"/sites/default/files/{year_month}/{year}{month}{day}_council_minutes.pdf",
                        f"/sites/default/files/{year_month}/council-meeting-agenda-{day}-{date.strftime('%B').lower()}-{year}.pdf",
                        f"/sites/default/files/{year_month}/council-meeting-minutes-{day}-{date.strftime('%B').lower()}-{year}.pdf",
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
                            print(f"    Found: {date_str} - {doc_type}")
        
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
            if not getattr(self, 'session', None):
                self.session = cloudscraper.create_scraper()
                self.session.headers.update(self.headers)
            r = self.session.get(url, headers=test_headers, timeout=8, allow_redirects=True)
            content_type = r.headers.get('Content-Type', '').lower()
            return r.status_code in (200, 206) and ('pdf' in content_type or url.lower().endswith('.pdf'))
        except:
            return False
    
    def scrape(self):
        """Scrape Stonnington using multiple approaches"""
        results = []
        
        # Approach 1: Try the main council website patterns
        print("  Trying Stonnington main website patterns...")
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
                (f"{base}/{year}/{dd}-{month_full}-{year}/council-meeting-agenda-{dd}-{month_full}-{year}.pdf", 'agenda'),
                (f"{base}/{year}/{dd}-{month_full}-{year}/council-meeting-minutes-{dd}-{month_full}-{year}.pdf", 'minutes'),
                (f"{base}/{year}/{dd}-{month_short}-{year}/council-meeting-agenda-{dd}-{month_short}-{year}.pdf", 'agenda'),
                (f"{base}/{year}/{dd}-{month_short}-{year}/council-meeting-minutes-{dd}-{month_short}-{year}.pdf", 'minutes'),
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
                    print(f"    Found: {date_str} - {doc_type}")
                    break  # Found a working pattern for this date
        
        # Approach 2: Try InfoCouncil pattern
        print("  Trying Stonnington InfoCouncil patterns...")
        
        # InfoCouncil commonly uses prefixes like OCM/CM/SCM and suffixes AGN/MIN
        # e.g., OCM_DDMMYYYY_AGN.PDF, CM_DDMMYYYY_MIN.PDF, ORD_DDMMYYYY_AGN_AT.PDF
        
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
            
            # Try both direct and redirect URLs with multiple codes
            prefixes = ["ORD", "OCM", "CM", "SCM"]
            agn_suffixes = ["AGN_AT.PDF", "AGN.PDF", "AGN_1.PDF"]
            min_suffixes = ["MIN.PDF", "MIN_1.PDF"]
            patterns = []
            for p in prefixes:
                for suf in agn_suffixes:
                    patterns.append((f"{self.infocouncil_base}/Open/{month_year}/{p}_{date_code}_{suf}", 'agenda'))
                for suf in min_suffixes:
                    patterns.append((f"{self.infocouncil_base}/Open/{month_year}/{p}_{date_code}_{suf}", 'minutes'))
            # Also try redirector links
            for p in prefixes:
                for suf in agn_suffixes:
                    patterns.append((f"{self.infocouncil_base}/RedirectToDoc.aspx?URL=Open/{month_year}/{p}_{date_code}_{suf}", 'agenda'))
                for suf in min_suffixes:
                    patterns.append((f"{self.infocouncil_base}/RedirectToDoc.aspx?URL=Open/{month_year}/{p}_{date_code}_{suf}", 'minutes'))
            
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
                    print(f"    Found (InfoCouncil): {date_str} - {doc_type}")
        
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


# Test the fixed scrapers
if __name__ == "__main__":
    print("=" * 60)
    print("TESTING FIXED SCRAPERS FOR YARRA AND STONNINGTON")
    print("=" * 60)
    
    total_docs = 0
    
    # Test Yarra
    print("\n1. YARRA CITY COUNCIL")
    print("-" * 40)
    try:
        scraper = YarraFixedScraper()
        docs = scraper.scrape()
        
        agendas = [d for d in docs if d.document_type == 'agenda']
        minutes = [d for d in docs if d.document_type == 'minutes']
        
        print(f"\n  Total: {len(docs)} documents ({len(agendas)} agendas, {len(minutes)} minutes)")
        
        if docs:
            print(f"  Most recent: {docs[0].date} - {docs[0].title[:50]}...")
            print(f"  URL: {docs[0].url}")
        
        total_docs += len(docs)
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    # Test Stonnington
    print("\n2. STONNINGTON CITY COUNCIL")
    print("-" * 40)
    try:
        scraper = StonningtonFixedScraper()
        docs = scraper.scrape()
        
        agendas = [d for d in docs if d.document_type == 'agenda']
        minutes = [d for d in docs if d.document_type == 'minutes']
        
        print(f"\n  Total: {len(docs)} documents ({len(agendas)} agendas, {len(minutes)} minutes)")
        
        if docs:
            print(f"  Most recent: {docs[0].date} - {docs[0].title[:50]}...")
            print(f"  URL: {docs[0].url}")
        
        total_docs += len(docs)
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"TOTAL FROM FIXED SCRAPERS: {total_docs} documents")
    
    if total_docs > 0:
        print("\n✅ SUCCESS! Fixed scrapers are working!")
        print("   Next step: Update m9_unified_scraper.py to use these fixed scrapers")
    else:
        print("\n⚠️  Still having issues - may need to check council websites manually")
    print("=" * 60)
