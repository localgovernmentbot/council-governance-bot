"""
Final M9 scrapers using exact URL patterns discovered
"""

import requests
from datetime import datetime, timedelta
from dateutil.parser import parse as parse_date
from m9_adapted import MeetingDocument, BaseM9Scraper


class YarraFixedScraper(BaseM9Scraper):
    """Yarra scraper using exact bucket pattern"""
    
    def __init__(self):
        super().__init__(
            council_id="YARR",
            council_name="Yarra City Council",
            base_url="https://www.yarracity.vic.gov.au"
        )
    
    def scrape(self):
        """Scrape Yarra using /sites/default/files/{YYYY-MM}/ pattern"""
        results = []
        
        # Check last 6 months
        current_date = datetime.now()
        
        for months_back in range(6):
            check_date = current_date - timedelta(days=30 * months_back)
            year_month = check_date.strftime("%Y-%m")
            
            # PDC meetings (fairly consistent pattern)
            # Try Tuesdays for PDC
            for day in range(1, 32):
                try:
                    meeting_date = datetime(check_date.year, check_date.month, day)
                    if meeting_date.weekday() == 1:  # Tuesday
                        date_str = meeting_date.strftime("%Y%m%d")
                        
                        # Try both hyphen and underscore patterns
                        pdc_patterns = [
                            f"{date_str}-pdc-agenda.pdf",
                            f"{date_str}_pdc_agenda.pdf"
                        ]
                        
                        for pattern in pdc_patterns:
                            url = f"{self.base_url}/sites/default/files/{year_month}/{pattern}"
                            try:
                                resp = requests.head(url, headers=self.headers, timeout=10)
                                if resp.status_code == 200:
                                    doc = MeetingDocument(
                                        council_id=self.council_id,
                                        council_name=self.council_name,
                                        document_type='agenda',
                                        meeting_type='planning',
                                        title=f"Planning Decisions Committee Agenda - {meeting_date.strftime('%Y-%m-%d')}",
                                        date=meeting_date.strftime('%Y-%m-%d'),
                                        url=url,
                                        webpage_url=self.base_url
                                    )
                                    results.append(doc)
                                    print(f"  Found PDC: {meeting_date.strftime('%Y-%m-%d')}")
                                    break
                            except:
                                pass
                        
                        # Council minutes patterns
                        minutes_patterns = [
                            f"{date_str}-council-minutes.pdf",
                            f"minutes_ordinary_council_meeting_{day}_{check_date.strftime('%B').lower()}_{check_date.year}.pdf",
                            f"public_minutes_tuesday_{day}_{check_date.strftime('%B').lower()}_{check_date.year}_with_attachments.pdf"
                        ]
                        
                        for pattern in minutes_patterns:
                            url = f"{self.base_url}/sites/default/files/{year_month}/{pattern}"
                            try:
                                resp = requests.head(url, headers=self.headers, timeout=10)
                                if resp.status_code == 200:
                                    doc = MeetingDocument(
                                        council_id=self.council_id,
                                        council_name=self.council_name,
                                        document_type='minutes',
                                        meeting_type='council',
                                        title=f"Council Meeting Minutes - {meeting_date.strftime('%Y-%m-%d')}",
                                        date=meeting_date.strftime('%Y-%m-%d'),
                                        url=url,
                                        webpage_url=self.base_url
                                    )
                                    results.append(doc)
                                    print(f"  Found minutes: {meeting_date.strftime('%Y-%m-%d')}")
                                    break
                            except:
                                pass
                except:
                    pass
        
        # Sort by date
        results.sort(key=lambda x: x.date, reverse=True)
        return results


class StonningtonFixedScraper(BaseM9Scraper):
    """Stonnington scraper using exact folder pattern"""
    
    def __init__(self):
        super().__init__(
            council_id="STON",
            council_name="Stonnington City Council",
            base_url="https://www.stonnington.vic.gov.au"
        )
    
    def scrape(self):
        """Scrape Stonnington using /files/assets/public/ folder pattern"""
        results = []
        
        # Based on schedule: bi-monthly meetings
        meeting_dates = [
            (2025, 8, 25), (2025, 8, 11), (2025, 7, 28),
            (2025, 6, 30), (2025, 6, 16), (2025, 5, 26),
            (2025, 5, 12), (2025, 4, 28), (2025, 4, 14),
            (2025, 3, 31), (2025, 3, 17), (2025, 2, 24)
        ]
        
        for year, month, day in meeting_dates:
            meeting_date = datetime(year, month, day)
            folder_date = meeting_date.strftime("%d-%B-%Y").lower()
            
            # Try common filename patterns
            filename_patterns = [
                "agenda.pdf",
                f"agenda-council-meeting-{day}-{meeting_date.strftime('%B').lower()}-{year}.pdf",
                f"council-meeting-agenda-{day}-{meeting_date.strftime('%B').lower()}-{year}.pdf",
                f"agenda-council_meeting_-_{day}_{meeting_date.strftime('%B').lower()}_{year}.pdf"
            ]
            
            for pattern in filename_patterns:
                url = f"{self.base_url}/files/assets/public/v/2/about/council-meetings/{year}/{folder_date}/{pattern}"
                try:
                    resp = requests.head(url, headers=self.headers, timeout=10)
                    if resp.status_code == 200:
                        doc = MeetingDocument(
                            council_id=self.council_id,
                            council_name=self.council_name,
                            document_type='agenda',
                            meeting_type='council',
                            title=f"Council Meeting Agenda - {meeting_date.strftime('%Y-%m-%d')}",
                            date=meeting_date.strftime('%Y-%m-%d'),
                            url=url,
                            webpage_url=self.base_url
                        )
                        results.append(doc)
                        print(f"  Found agenda: {meeting_date.strftime('%Y-%m-%d')}")
                        break
                except:
                    pass
            
            # Try minutes patterns
            minutes_patterns = [
                "minutes.pdf",
                f"council-meeting-minutes-{day}-{meeting_date.strftime('%B').lower()}-{year}.pdf",
                f"minutes-council-meeting-{day}-{meeting_date.strftime('%B').lower()}-{year}.pdf"
            ]
            
            for pattern in minutes_patterns:
                url = f"{self.base_url}/files/assets/public/v/2/about/council-meetings/{year}/{folder_date}/{pattern}"
                try:
                    resp = requests.head(url, headers=self.headers, timeout=10)
                    if resp.status_code == 200:
                        doc = MeetingDocument(
                            council_id=self.council_id,
                            council_name=self.council_name,
                            document_type='minutes',
                            meeting_type='council',
                            title=f"Council Meeting Minutes - {meeting_date.strftime('%Y-%m-%d')}",
                            date=meeting_date.strftime('%Y-%m-%d'),
                            url=url,
                            webpage_url=self.base_url
                        )
                        results.append(doc)
                        print(f"  Found minutes: {meeting_date.strftime('%Y-%m-%d')}")
                        break
                except:
                    pass
        
        # Sort by date
        results.sort(key=lambda x: x.date, reverse=True)
        return results


class PortPhillipFixedScraper(BaseM9Scraper):
    """Port Phillip scraper using exact InfoCouncil pattern"""
    
    def __init__(self):
        super().__init__(
            council_id="PORT",
            council_name="Port Phillip City Council",
            base_url="https://portphillip.infocouncil.biz"
        )
    
    def scrape(self):
        """Scrape Port Phillip using exact InfoCouncil pattern"""
        results = []
        
        # Known meeting dates from schedule
        meeting_dates = [
            (2025, 9, 2), (2025, 8, 20), (2025, 8, 6),
            (2025, 7, 2), (2025, 6, 18), (2025, 5, 21),
            (2025, 5, 7), (2025, 4, 16), (2025, 3, 19),
            (2025, 3, 5), (2025, 2, 19), (2025, 2, 5)
        ]
        
        for year, month, day in meeting_dates:
            meeting_date = datetime(year, month, day)
            date_str = meeting_date.strftime("%d%m%Y")
            month_year = meeting_date.strftime("%Y/%m")
            
            # Ordinary meeting URLs
            agenda_url = f"{self.base_url}/Open/{month_year}/ORD_{date_str}_AGN_AT.PDF"
            minutes_url = f"{self.base_url}/Open/{month_year}/ORD_{date_str}_MIN.PDF"
            
            # Check agenda
            try:
                resp = requests.head(agenda_url, headers=self.headers, timeout=10, allow_redirects=True)
                if resp.status_code == 200 and 'pdf' in resp.headers.get('Content-Type', '').lower():
                    doc = MeetingDocument(
                        council_id=self.council_id,
                        council_name=self.council_name,
                        document_type='agenda',
                        meeting_type='ordinary',
                        title=f"Ordinary Council Meeting Agenda - {meeting_date.strftime('%Y-%m-%d')}",
                        date=meeting_date.strftime('%Y-%m-%d'),
                        url=agenda_url,
                        webpage_url=self.base_url
                    )
                    results.append(doc)
                    print(f"  Found: {meeting_date.strftime('%Y-%m-%d')} - agenda")
            except:
                pass
            
            # Check minutes
            try:
                resp = requests.head(minutes_url, headers=self.headers, timeout=10, allow_redirects=True)
                if resp.status_code == 200 and 'pdf' in resp.headers.get('Content-Type', '').lower():
                    doc = MeetingDocument(
                        council_id=self.council_id,
                        council_name=self.council_name,
                        document_type='minutes',
                        meeting_type='ordinary',
                        title=f"Ordinary Council Meeting Minutes - {meeting_date.strftime('%Y-%m-%d')}",
                        date=meeting_date.strftime('%Y-%m-%d'),
                        url=minutes_url,
                        webpage_url=self.base_url
                    )
                    results.append(doc)
                    print(f"  Found: {meeting_date.strftime('%Y-%m-%d')} - minutes")
            except:
                pass
        
        # Sort by date
        results.sort(key=lambda x: x.date, reverse=True)
        return results


# Test all three
if __name__ == "__main__":
    print("Testing Fixed M9 Scrapers with Exact Patterns")
    print("=" * 60)
    
    scrapers = [
        ("Yarra", YarraFixedScraper),
        ("Stonnington", StonningtonFixedScraper),
        ("Port Phillip", PortPhillipFixedScraper),
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
            
            total_docs += len(docs)
            
        except Exception as e:
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print(f"Total from these scrapers: {total_docs} documents")
