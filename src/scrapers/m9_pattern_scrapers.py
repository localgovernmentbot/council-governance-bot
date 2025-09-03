"""
Final M9 scrapers using discovered patterns
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from dateutil.parser import parse as parse_date
from typing import List
from m9_adapted import MeetingDocument, BaseM9Scraper


class YarraPatternScraper(BaseM9Scraper):
    """Yarra scraper using YIMBY's discovered pattern"""
    
    def __init__(self):
        super().__init__(
            council_id="YARR",
            council_name="Yarra City Council",
            base_url="https://www.yarracity.vic.gov.au"
        )
    
    def scrape(self):
        """Use YIMBY's approach - look for upcoming meetings"""
        results = []
        
        # YIMBY's URL
        url = "https://www.yarracity.vic.gov.au/about-us/council-and-committee-meetings/upcoming-council-and-committee-meetings"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # YIMBY looks for this specific div
                agenda_list = soup.find("div", class_="show-for-medium-up")
                
                if agenda_list:
                    # Find all links in this div
                    for link in agenda_list.find_all("a", href=True):
                        href = link.get('href', '')
                        text = link.get_text(strip=True)
                        
                        # Extract date
                        date_str = self.extract_date(text)
                        if date_str:
                            # Make URL absolute
                            if not href.startswith('http'):
                                href = self.base_url + href
                            
                            # Try to fetch the meeting page to get agenda link
                            try:
                                meeting_response = requests.get(href, headers=self.headers, timeout=30)
                                if meeting_response.status_code == 200:
                                    meeting_soup = BeautifulSoup(meeting_response.text, 'html.parser')
                                    
                                    # Look for download link
                                    download_link = meeting_soup.find("a", class_="download-link")
                                    if download_link:
                                        download_url = download_link.get('href', '')
                                        if not download_url.startswith('http'):
                                            download_url = self.base_url + download_url
                                        
                                        # Get title
                                        title = meeting_soup.find("h1", class_="heading")
                                        title_text = title.text if title else text
                                        
                                        doc = MeetingDocument(
                                            council_id=self.council_id,
                                            council_name=self.council_name,
                                            document_type='agenda',
                                            meeting_type='council',
                                            title=title_text,
                                            date=date_str,
                                            url=download_url,
                                            webpage_url=href
                                        )
                                        results.append(doc)
                            except:
                                pass
                
                # Also try main meetings page
                main_url = "https://www.yarracity.vic.gov.au/about-us/council-and-committee-meetings"
                response2 = requests.get(main_url, headers=self.headers, timeout=30)
                
                if response2.status_code == 200:
                    soup2 = BeautifulSoup(response2.text, 'html.parser')
                    
                    # Look for any PDF links
                    for link in soup2.find_all('a', href=lambda x: x and '.pdf' in x.lower()):
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
                                    webpage_url=main_url
                                )
                                results.append(doc)
                                
        except Exception as e:
            print(f"  Error: {e}")
        
        # Sort by date
        results.sort(key=lambda x: x.date, reverse=True)
        
        return results


class PortPhillipYearScraper(BaseM9Scraper):
    """Port Phillip scraper using year-based URLs"""
    
    def __init__(self):
        super().__init__(
            council_id="PORT",
            council_name="Port Phillip City Council",
            base_url="https://www.portphillip.vic.gov.au"
        )
    
    def scrape(self):
        """Scrape Port Phillip using year-based pages"""
        results = []
        
        # Try current and previous year
        current_year = datetime.now().year
        years = [current_year, current_year - 1]
        
        for year in years:
            url = f"{self.base_url}/about-the-council/council-meetings/{year}-meetings-and-agendas"
            
            try:
                response = requests.get(url, headers=self.headers, timeout=30)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find all PDF links
                    for link in soup.find_all('a', href=lambda x: x and '.pdf' in x.lower()):
                        href = link.get('href', '')
                        text = link.get_text(strip=True)
                        
                        # Check if it's an agenda or minutes
                        if any(word in text.lower() for word in ['agenda', 'minutes', 'report']):
                            date_str = self.extract_date(text)
                            if date_str:
                                doc_type = self.determine_doc_type(text)
                                
                                if not href.startswith('http'):
                                    href = self.base_url + href
                                
                                doc = MeetingDocument(
                                    council_id=self.council_id,
                                    council_name=self.council_name,
                                    document_type=doc_type or 'agenda',
                                    meeting_type=self.determine_meeting_type(text),
                                    title=text,
                                    date=date_str,
                                    url=href,
                                    webpage_url=url
                                )
                                results.append(doc)
                    
                    print(f"  Found {len([d for d in results if str(year) in d.date])} documents for {year}")
                    
                elif response.status_code == 404:
                    # Try without year in URL
                    base_meetings_url = f"{self.base_url}/about-the-council/meetings-and-minutes"
                    response = requests.get(base_meetings_url, headers=self.headers, timeout=30)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Look for year links
                        for link in soup.find_all('a', href=True):
                            if str(year) in link.get('href', '') or str(year) in link.get_text(strip=True):
                                year_url = link.get('href', '')
                                if not year_url.startswith('http'):
                                    year_url = self.base_url + year_url
                                
                                # Fetch year page
                                try:
                                    year_response = requests.get(year_url, headers=self.headers, timeout=30)
                                    if year_response.status_code == 200:
                                        year_soup = BeautifulSoup(year_response.text, 'html.parser')
                                        
                                        # Extract PDFs from year page
                                        for pdf_link in year_soup.find_all('a', href=lambda x: x and '.pdf' in x.lower()):
                                            href = pdf_link.get('href', '')
                                            text = pdf_link.get_text(strip=True)
                                            
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
                                                        meeting_type=self.determine_meeting_type(text),
                                                        title=text,
                                                        date=date_str,
                                                        url=href,
                                                        webpage_url=year_url
                                                    )
                                                    results.append(doc)
                                except:
                                    pass
                                    
            except Exception as e:
                print(f"  Error for year {year}: {e}")
        
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


class StonningtonInfoCouncilScraper(BaseM9Scraper):
    """Stonnington scraper using InfoCouncil year patterns"""
    
    def __init__(self):
        super().__init__(
            council_id="STON",
            council_name="Stonnington City Council",
            base_url="https://stonnington.infocouncil.biz"
        )
    
    def scrape(self):
        """Scrape Stonnington InfoCouncil with year patterns"""
        results = []
        
        # Try different year patterns
        current_year = datetime.now().year
        years = [current_year - 1, current_year]  # 2024, 2025
        
        for year in years:
            # InfoCouncil patterns
            urls = [
                f"{self.base_url}/Open/{year}/",
                f"{self.base_url}/Open/{year}/OM_{year}/",
                f"{self.base_url}/committee.aspx?id={year}"
            ]
            
            for url in urls:
                try:
                    response = requests.get(url, headers=self.headers, timeout=30)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Look for meeting links
                        for link in soup.find_all('a', href=True):
                            href = link.get('href', '')
                            text = link.get_text(strip=True)
                            
                            # Check for meeting patterns
                            if any(pattern in href.lower() for pattern in ['.pdf', 'meeting.aspx', 'download.aspx']):
                                if any(word in text.lower() for word in ['council', 'meeting', 'agenda', 'minutes']):
                                    date_str = self.extract_date(text)
                                    if not date_str:
                                        # Try extracting from href
                                        date_match = re.search(r'(\d{1,2}[-_]\w+[-_]\d{4}|\d{8})', href)
                                        if date_match:
                                            date_str = self.extract_date(date_match.group())
                                    
                                    if date_str:
                                        doc_type = self.determine_doc_type(text) or 'agenda'
                                        
                                        if not href.startswith('http'):
                                            href = self.base_url + '/' + href.lstrip('/')
                                        
                                        doc = MeetingDocument(
                                            council_id=self.council_id,
                                            council_name=self.council_name,
                                            document_type=doc_type,
                                            meeting_type='council',
                                            title=text or f"Council Meeting {doc_type.title()} - {date_str}",
                                            date=date_str,
                                            url=href,
                                            webpage_url=url
                                        )
                                        results.append(doc)
                        
                        print(f"  Found {len([d for d in results if str(year) in d.date])} documents for {year}")
                        
                except Exception as e:
                    pass
        
        # Also try base URL
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for recent meetings on homepage
                for link in soup.find_all('a', href=lambda x: x and any(p in x.lower() for p in ['.pdf', 'open/', 'meeting'])):
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    if any(word in text.lower() for word in ['agenda', 'minutes']):
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
