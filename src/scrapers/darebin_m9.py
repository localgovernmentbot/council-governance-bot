"""
Darebin City Council Scraper for M9 Bot
Adapted from our working scraper
"""

from bs4 import BeautifulSoup
import re
from datetime import datetime
from dateutil.parser import parse as parse_date
from dataclasses import dataclass
from typing import Optional, List
import requests
import cloudscraper
from src.utils.infocouncil import discover_month_files, parse_infocouncil_filename


@dataclass
class MeetingDocument:
    """Data class for meeting documents"""
    council_id: str
    council_name: str
    document_type: str  # agenda, minutes
    meeting_type: str   # council, delegated, special
    title: str
    date: str          # YYYY-MM-DD format
    url: str
    webpage_url: str


class DarebinScraper:
    """Scraper for Darebin City Council"""
    
    def __init__(self):
        self.council_id = "DARE"
        self.council_name = "Darebin City Council"
        self.base_url = "https://www.darebin.vic.gov.au"
        # Using the specific 2025 page that has direct PDFs
        self.meetings_url = "https://www.darebin.vic.gov.au/About-council/Council-structure-and-performance/Council-and-Committee-Meetings/Council-meetings/Meeting-agendas-and-minutes/2025-Council-meeting-agendas-and-minutes"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-AU,en;q=0.9',
        }
        try:
            self.session = cloudscraper.create_scraper()
            self.session.headers.update(self.headers)
        except Exception:
            self.session = requests.Session()
            self.session.headers.update(self.headers)
    
    def fetch_page(self, url: str) -> str:
        """Fetch a page using a session to handle 403s and redirects"""
        try:
            # Include referer to simulate navigation from site
            headers = dict(self.headers)
            headers['Referer'] = self.base_url
            resp = self.session.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return ""
    
    def extract_date(self, text: str) -> Optional[str]:
        """Extract date from text and return in YYYY-MM-DD format"""
        date_patterns = [
            r'\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}',
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'\d{1,2}-\d{1,2}-\d{4}',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    parsed = parse_date(match.group())
                    return parsed.strftime('%Y-%m-%d')
                except:
                    continue
        return ""
    
    def clean_title(self, title: str) -> str:
        """Clean up document titles"""
        title = re.sub(r'\(PDF,\s*[\d\.]+\s*(KB|MB|GB)\)', '', title).strip()
        title = re.sub(r'pdf\s+[\d\.]+\s*(KB|MB|GB)', '', title, flags=re.IGNORECASE).strip()
        title = re.sub(r'\.pdf$', '', title, flags=re.IGNORECASE).strip()
        return title
    
    def determine_meeting_type(self, text: str) -> str:
        """Determine meeting type from text"""
        text_lower = text.lower()
        
        if 'delegated' in text_lower or 'committee' in text_lower:
            return 'delegated'
        elif 'special' in text_lower:
            return 'special'
        else:
            return 'council'
    
    def determine_doc_type(self, text: str) -> str:
        """Determine if document is agenda or minutes"""
        text_lower = text.lower()
        
        if 'minutes' in text_lower:
            return 'minutes'
        elif 'agenda' in text_lower:
            return 'agenda'
        else:
            return None
    
    def _probe_infocouncil(self) -> List[MeetingDocument]:
        """Fallback: probe InfoCouncil-style URLs if the main site blocks us.

        Attempts Tuesday and Monday for recent weeks and checks for
        ORD/OCM prefixes with AGN/MIN suffixes.
        """
        base = "https://darebin.infocouncil.biz"
        out: List[MeetingDocument] = []
        today = datetime.now()
        from datetime import timedelta
        for weeks_back in range(0, 26):  # ~6 months
            d = today - timedelta(weeks=weeks_back)
            # Try likely meeting days: Tue, Mon, Wed, Thu
            for offset in (1, 0, 2, 3):
                target = d - timedelta(days=(d.weekday() - offset) % 7)
                date_code = target.strftime("%d%m%Y")
                month_year = target.strftime("%Y/%m")
                formatted = target.strftime('%Y-%m-%d')
                prefixes = ["ORD", "OCM", "CM"]
                files = [(f"{p}_{date_code}_AGN_AT.PDF", 'agenda') for p in prefixes] + \
                        [(f"{p}_{date_code}_AGN.PDF", 'agenda') for p in prefixes] + \
                        [(f"{p}_{date_code}_MIN.PDF", 'minutes') for p in prefixes]
                for fname, kind in files:
                    direct = f"{base}/Open/{month_year}/{fname}"
                    redir = f"{base}/RedirectToDoc.aspx?URL=Open/{month_year}/{fname}"
                    try:
                        r = self.session.get(direct, headers={'Range': 'bytes=0-0', **self.headers}, timeout=8, allow_redirects=True)
                        if r.status_code in (200, 206) and 'pdf' in r.headers.get('Content-Type', '').lower():
                            out.append(MeetingDocument(
                                council_id=self.council_id,
                                council_name=self.council_name,
                                document_type=kind,
                                meeting_type='council',
                                title=f"Council Meeting {kind.title()} - {formatted}",
                                date=formatted,
                                url=direct,
                                webpage_url=base,
                            ))
                            continue
                        # Try redirector
                        r2 = self.session.get(redir, headers={'Range': 'bytes=0-0', **self.headers}, timeout=8, allow_redirects=True)
                        if r2.status_code in (200, 206) and 'pdf' in r2.headers.get('Content-Type', '').lower():
                            out.append(MeetingDocument(
                                council_id=self.council_id,
                                council_name=self.council_name,
                                document_type=kind,
                                meeting_type='council',
                                title=f"Council Meeting {kind.title()} - {formatted}",
                                date=formatted,
                                url=redir,
                                webpage_url=base,
                            ))
                    except Exception:
                        pass
        # Try month discovery if nothing found yet (last 6 months)
        if not out:
            from datetime import timedelta
            for i in range(0, 6):
                dt = datetime.now() - timedelta(days=30*i)
                files = discover_month_files(base, dt.year, dt.month, self.session, self.headers)
                for u in files:
                    kind, iso = parse_infocouncil_filename(u)
                    if not kind or not iso:
                        continue
                    out.append(MeetingDocument(
                        council_id=self.council_id,
                        council_name=self.council_name,
                        document_type=kind,
                        meeting_type='council',
                        title=f"Council Meeting {kind.title()} - {iso}",
                        date=iso,
                        url=u,
                        webpage_url=base,
                    ))

        # Dedupe
        seen = set(); uniq = []
        for d in out:
            if d.url not in seen:
                seen.add(d.url); uniq.append(d)
        uniq.sort(key=lambda x: x.date, reverse=True)
        return uniq

    def scrape(self):
        """Scrape Darebin council meetings"""
        results: List[MeetingDocument] = []
        
        html = self.fetch_page(self.meetings_url)
        if not html:
            # Fallback
            return self._probe_infocouncil()
        
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
        
        # If blocked or empty, try InfoCouncil fallback
        return results or self._probe_infocouncil()
