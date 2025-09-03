"""
Port Phillip City Council scraper with timeout handling and multiple strategies
"""

import requests
from bs4 import BeautifulSoup
import asyncio
import aiohttp
from datetime import datetime, timedelta
import re
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from base_m9 import MeetingDocument, BaseM9Scraper


class PortPhillipEnhancedScraper(BaseM9Scraper):
    """Port Phillip scraper with timeout handling and multiple approaches"""
    
    def __init__(self):
        super().__init__(
            council_id="PORT",
            council_name="Port Phillip City Council",
            base_url="https://www.portphillip.vic.gov.au"
        )
        self.timeout = 5  # Short timeout
        self.max_retries = 3
        
    def try_url_with_timeout(self, url, timeout=5):
        """Try to fetch URL with timeout and retries"""
        for attempt in range(self.max_retries):
            try:
                # Use shorter timeout
                response = requests.get(
                    url, 
                    headers=self.headers,
                    timeout=timeout,
                    allow_redirects=True,
                    stream=True  # Stream for large responses
                )
                
                if response.status_code == 200:
                    return response
                    
            except requests.Timeout:
                print(f"  Timeout attempt {attempt + 1} for {url[:50]}...")
                timeout = timeout * 1.5  # Increase timeout each retry
                
            except Exception as e:
                print(f"  Error attempt {attempt + 1}: {str(e)[:50]}")
                
        return None
    
    def scrape_infocouncil(self):
        """Try InfoCouncil pattern (they might use this system)"""
        results = []
        base_url = "https://portphillip.infocouncil.biz"
        
        # Port Phillip meets on Wednesdays typically
        current_date = datetime.now()
        
        for weeks_back in range(12):  # Check last 3 months
            check_date = current_date - timedelta(weeks=weeks_back)
            
            # Find Wednesday
            days_to_wednesday = (2 - check_date.weekday()) % 7
            wednesday = check_date + timedelta(days=days_to_wednesday)
            
            # Also check Tuesday (alternative meeting day)
            tuesday = wednesday - timedelta(days=1)
            
            for meeting_day in [wednesday, tuesday]:
                date_str = meeting_day.strftime("%d%m%Y")
                formatted_date = meeting_day.strftime("%Y-%m-%d")
                month_year = meeting_day.strftime("%Y/%m")
                
                # Try different URL patterns
                patterns = [
                    f"{base_url}/Open/{month_year}/ORD_{date_str}_AGN_AT.PDF",
                    f"{base_url}/Open/{month_year}/ORD_{date_str}_MIN.PDF",
                    f"{base_url}/RedirectToDoc.aspx?URL=Open/{month_year}/ORD_{date_str}_AGN_AT.PDF",
                    f"{base_url}/RedirectToDoc.aspx?URL=Open/{month_year}/ORD_{date_str}_MIN.PDF",
                ]
                
                for url in patterns:
                    try:
                        # Quick HEAD request to check existence
                        response = requests.head(
                            url,
                            headers=self.headers,
                            timeout=3,
                            allow_redirects=True
                        )
                        
                        if response.status_code == 200:
                            content_type = response.headers.get('Content-Type', '')
                            if 'pdf' in content_type.lower():
                                doc_type = 'minutes' if '_MIN' in url else 'agenda'
                                
                                doc = MeetingDocument(
                                    council_id=self.council_id,
                                    council_name=self.council_name,
                                    document_type=doc_type,
                                    meeting_type='ordinary',
                                    title=f"Council Meeting {doc_type.title()} - {formatted_date}",
                                    date=formatted_date,
                                    url=url,
                                    webpage_url=base_url
                                )
                                results.append(doc)
                                print(f"  Found: {formatted_date} - {doc_type}")
                                
                    except:
                        pass
        
        return results
    
    def scrape_main_site(self):
        """Scrape main Port Phillip website with timeout handling"""
        results = []
        
        # Try different URLs
        urls = [
            "https://www.portphillip.vic.gov.au/about-the-council/meetings-and-minutes",
            "https://www.portphillip.vic.gov.au/about-the-council/governance-and-meetings",
            "https://www.portphillip.vic.gov.au/council-meetings"
        ]
        
        for url in urls:
            response = self.try_url_with_timeout(url, timeout=5)
            
            if response:
                try:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for PDF links
                    for link in soup.find_all('a', href=True):
                        href = link.get('href', '')
                        text = link.get_text(strip=True)
                        
                        if '.pdf' in href.lower():
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
                                    webpage_url=url
                                )
                                results.append(doc)
                                
                except Exception as e:
                    print(f"  Error parsing response: {e}")
        
        return results
    
    async def async_scrape(self):
        """Asynchronous scraping for better timeout handling"""
        results = []
        
        async with aiohttp.ClientSession() as session:
            urls = [
                "https://www.portphillip.vic.gov.au/about-the-council/meetings-and-minutes",
                "https://portphillip.infocouncil.biz",
                "https://www.portphillip.vic.gov.au/council-meetings"
            ]
            
            for url in urls:
                try:
                    async with session.get(
                        url,
                        headers=self.headers,
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        
                        if response.status == 200:
                            text = await response.text()
                            soup = BeautifulSoup(text, 'html.parser')
                            
                            # Process links
                            for link in soup.find_all('a', href=True):
                                href = link.get('href', '')
                                link_text = link.get_text(strip=True)
                                
                                if '.pdf' in href.lower():
                                    date_str = self.extract_date(link_text)
                                    if date_str:
                                        doc_type = self.determine_doc_type(link_text)
                                        
                                        if not href.startswith('http'):
                                            if 'infocouncil' in url:
                                                href = "https://portphillip.infocouncil.biz" + href
                                            else:
                                                href = self.base_url + href
                                        
                                        doc = MeetingDocument(
                                            council_id=self.council_id,
                                            council_name=self.council_name,
                                            document_type=doc_type or 'agenda',
                                            meeting_type='council',
                                            title=link_text,
                                            date=date_str,
                                            url=href,
                                            webpage_url=url
                                        )
                                        results.append(doc)
                                        
                except asyncio.TimeoutError:
                    print(f"  Async timeout for {url}")
                except Exception as e:
                    print(f"  Async error: {e}")
        
        return results
    
    def scrape_with_threading(self):
        """Use threading to handle multiple requests in parallel"""
        results = []
        
        def fetch_url(url):
            try:
                response = requests.get(url, headers=self.headers, timeout=5)
                if response.status_code == 200:
                    return response.text
            except:
                return None
            return None
        
        urls = [
            "https://www.portphillip.vic.gov.au/about-the-council/meetings-and-minutes",
            "https://portphillip.infocouncil.biz",
            "https://portphillip.infocouncil.biz/Open/"
        ]
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(fetch_url, url): url for url in urls}
            
            for future in futures:
                url = futures[future]
                try:
                    html = future.result(timeout=10)
                    if html:
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        for link in soup.find_all('a', href=True):
                            href = link.get('href', '')
                            text = link.get_text(strip=True)
                            
                            if '.pdf' in href.lower():
                                date_str = self.extract_date(text)
                                if date_str:
                                    doc_type = self.determine_doc_type(text)
                                    
                                    if not href.startswith('http'):
                                        if 'infocouncil' in url:
                                            href = "https://portphillip.infocouncil.biz" + href
                                        else:
                                            href = self.base_url + href
                                    
                                    doc = MeetingDocument(
                                        council_id=self.council_id,
                                        council_name=self.council_name,
                                        document_type=doc_type or 'agenda',
                                        meeting_type='council',
                                        title=text,
                                        date=date_str,
                                        url=href,
                                        webpage_url=url
                                    )
                                    results.append(doc)
                                    
                except TimeoutError:
                    print(f"  Thread timeout for {url}")
                except Exception as e:
                    print(f"  Thread error: {e}")
        
        return results
    
    def scrape(self):
        """Main scrape method trying multiple strategies"""
        all_results = []
        
        print("  Strategy 1: InfoCouncil pattern...")
        results = self.scrape_infocouncil()
        all_results.extend(results)
        print(f"    Found {len(results)} documents")
        
        if len(all_results) < 5:
            print("  Strategy 2: Main site with timeout handling...")
            results = self.scrape_main_site()
            all_results.extend(results)
            print(f"    Found {len(results)} documents")
        
        if len(all_results) < 5:
            print("  Strategy 3: Threading approach...")
            results = self.scrape_with_threading()
            all_results.extend(results)
            print(f"    Found {len(results)} documents")
        
        if len(all_results) < 5:
            print("  Strategy 4: Async approach...")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(self.async_scrape())
            all_results.extend(results)
            print(f"    Found {len(results)} documents")
        
        # Remove duplicates
        seen_urls = set()
        unique_results = []
        for doc in all_results:
            if doc.url not in seen_urls:
                seen_urls.add(doc.url)
                unique_results.append(doc)
        
        # Sort by date
        unique_results.sort(key=lambda x: x.date, reverse=True)
        
        return unique_results


if __name__ == "__main__":
    print("Testing Port Phillip Enhanced Scraper")
    print("=" * 60)
    
    scraper = PortPhillipEnhancedScraper()
    docs = scraper.scrape()
    
    print(f"\nTotal documents found: {len(docs)}")
    
    if docs:
        agendas = [d for d in docs if d.document_type == 'agenda']
        minutes = [d for d in docs if d.document_type == 'minutes']
        
        print(f"  Agendas: {len(agendas)}")
        print(f"  Minutes: {len(minutes)}")
        
        print("\nMost recent documents:")
        for doc in docs[:5]:
            print(f"  - {doc.date}: {doc.title[:50]}...")
            print(f"    URL: {doc.url[:80]}...")
