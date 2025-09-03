"""
Advanced M9 Scrapers for Problematic Councils
Using proven GitHub solutions:
1. Yarra - SeleniumBase with stealth mode
2. Port Phillip - Extended timeouts + retry logic
3. Stonnington - Cloudscraper fallback
"""

import time
import re
from datetime import datetime
from dateutil.parser import parse as parse_date
from dataclasses import dataclass
from typing import Optional, List
import requests
from bs4 import BeautifulSoup

# Advanced imports
from seleniumbase import SB  # SeleniumBase for Cloudflare bypass
import cloudscraper  # Alternative Cloudflare bypass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import undetected_chromedriver as uc

from m9_adapted import MeetingDocument, BaseM9Scraper


class YarraAdvancedScraper(BaseM9Scraper):
    """Yarra scraper using SeleniumBase to bypass Cloudflare"""
    
    def __init__(self):
        super().__init__(
            council_id="YARR",
            council_name="Yarra City Council",
            base_url="https://www.yarracity.vic.gov.au"
        )
    
    def scrape(self):
        """Scrape Yarra using SeleniumBase with stealth mode"""
        results = []
        
        # Use SeleniumBase with UC mode (undetected Chrome)
        with SB(uc=True, headless=False) as sb:
            try:
                # Try the main meetings page
                url = "https://www.yarracity.vic.gov.au/about-us/council-and-committee-meetings"
                sb.open(url)
                sb.sleep(3)  # Let page fully load
                
                # Get page source
                soup = BeautifulSoup(sb.get_page_source(), 'html.parser')
                
                # Look for meeting links or documents
                all_links = soup.find_all('a', href=True)
                
                for link in all_links:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    # Check for PDF links or meeting pages
                    if '.pdf' in href.lower() or any(word in text.lower() for word in ['agenda', 'minutes']):
                        # Extract date
                        date_str = self.extract_date(text)
                        if not date_str:
                            continue
                        
                        # Determine document type
                        doc_type = self.determine_doc_type(text)
                        if not doc_type:
                            if '.pdf' in href.lower():
                                doc_type = 'agenda'  # Default for PDFs
                            else:
                                continue
                        
                        # Make URL absolute
                        if not href.startswith('http'):
                            href = self.base_url + href
                        
                        doc = MeetingDocument(
                            council_id=self.council_id,
                            council_name=self.council_name,
                            document_type=doc_type,
                            meeting_type=self.determine_meeting_type(text),
                            title=text,
                            date=date_str,
                            url=href,
                            webpage_url=url
                        )
                        results.append(doc)
                
                # If no results, try upcoming meetings page
                if not results:
                    print("  Trying upcoming meetings page...")
                    url2 = "https://www.yarracity.vic.gov.au/about-us/council-and-committee-meetings/upcoming-council-and-committee-meetings"
                    sb.open(url2)
                    sb.sleep(3)
                    
                    soup = BeautifulSoup(sb.get_page_source(), 'html.parser')
                    
                    # Look for meeting cards or sections
                    meeting_sections = soup.find_all(['div', 'section'], class_=re.compile(r'meeting|event|card', re.I))
                    
                    for section in meeting_sections:
                        section_text = section.get_text(strip=True)
                        date_str = self.extract_date(section_text)
                        
                        if date_str:
                            # Find links within this section
                            for link in section.find_all('a', href=True):
                                href = link.get('href', '')
                                text = link.get_text(strip=True)
                                
                                if any(word in text.lower() for word in ['agenda', 'minutes', 'download']):
                                    doc_type = self.determine_doc_type(text) or 'agenda'
                                    
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
                                        webpage_url=url2
                                    )
                                    results.append(doc)
                    
            except Exception as e:
                print(f"    SeleniumBase error: {e}")
                
                # Fallback to cloudscraper
                print("    Trying cloudscraper fallback...")
                try:
                    scraper = cloudscraper.create_scraper()
                    response = scraper.get(self.base_url + "/about-us/council-and-committee-meetings")
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Basic PDF search
                        for link in soup.find_all('a', href=lambda x: x and '.pdf' in x.lower()):
                            href = link.get('href', '')
                            text = link.get_text(strip=True)
                            date_str = self.extract_date(text)
                            
                            if date_str:
                                doc_type = self.determine_doc_type(text) or 'agenda'
                                
                                if not href.startswith('http'):
                                    href = self.base_url + href
                                
                                doc = MeetingDocument(
                                    council_id=self.council_id,
                                    council_name=self.council_name,
                                    document_type=doc_type,
                                    meeting_type='council',
                                    title=text,
                                    date=date_str,
                                    url=href,
                                    webpage_url=response.url
                                )
                                results.append(doc)
                except Exception as e2:
                    print(f"    Cloudscraper also failed: {e2}")
        
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


class PortPhillipAdvancedScraper(BaseM9Scraper):
    """Port Phillip scraper with extended timeouts and retry logic"""
    
    def __init__(self):
        super().__init__(
            council_id="PORT",
            council_name="Port Phillip City Council",
            base_url="https://www.portphillip.vic.gov.au"
        )
    
    def scrape(self):
        """Scrape Port Phillip with patience and retries"""
        results = []
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # Setup Chrome with extended timeouts
                options = webdriver.ChromeOptions()
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_argument('--headless')
                options.page_load_strategy = 'none'  # Don't wait for full page load
                
                driver = webdriver.Chrome(options=options)
                driver.set_page_load_timeout(120)  # 2 minutes timeout
                
                try:
                    url = "https://www.portphillip.vic.gov.au/about-the-council/meetings-and-minutes"
                    print(f"  Attempt {attempt + 1}: Loading Port Phillip (extended timeout)...")
                    
                    driver.get(url)
                    
                    # Wait for any content to appear
                    wait = WebDriverWait(driver, 60)
                    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                    
                    # Additional wait for dynamic content
                    time.sleep(10)
                    
                    # Execute JavaScript to stop loading if still pending
                    driver.execute_script("window.stop();")
                    
                    # Get whatever loaded
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    
                    # Look for any links
                    all_links = soup.find_all('a', href=True)
                    print(f"    Found {len(all_links)} total links")
                    
                    # Search for meeting-related content
                    for link in all_links:
                        href = link.get('href', '')
                        text = link.get_text(strip=True)
                        
                        # Look for PDFs or meeting keywords
                        if ('.pdf' in href.lower() or 
                            any(word in text.lower() for word in ['agenda', 'minutes', 'meeting'])):
                            
                            date_str = self.extract_date(text)
                            if date_str:
                                doc_type = self.determine_doc_type(text)
                                if not doc_type and '.pdf' in href.lower():
                                    doc_type = 'agenda'
                                
                                if doc_type:
                                    if not href.startswith('http'):
                                        href = self.base_url + href
                                    
                                    doc = MeetingDocument(
                                        council_id=self.council_id,
                                        council_name=self.council_name,
                                        document_type=doc_type,
                                        meeting_type=self.determine_meeting_type(text),
                                        title=text,
                                        date=date_str,
                                        url=href,
                                        webpage_url=url
                                    )
                                    results.append(doc)
                    
                    if results:
                        print(f"    Success! Found {len(results)} documents")
                        break
                    else:
                        print("    No documents found, retrying...")
                        
                finally:
                    driver.quit()
                    
            except TimeoutException:
                print(f"    Timeout on attempt {attempt + 1}")
            except Exception as e:
                print(f"    Error on attempt {attempt + 1}: {e}")
            
            if attempt < max_retries - 1:
                time.sleep(5)  # Wait before retry
        
        # Sort by date
        results.sort(key=lambda x: x.date, reverse=True)
        
        return results


class StonningtonAdvancedScraper(BaseM9Scraper):
    """Stonnington scraper using multiple approaches"""
    
    def __init__(self):
        super().__init__(
            council_id="STON",
            council_name="Stonnington City Council",
            base_url="https://www.stonnington.vic.gov.au"
        )
        # Also set InfoCouncil URL
        self.infocouncil_url = "https://stonnington.infocouncil.biz"
    
    def scrape(self):
        """Scrape Stonnington using multiple approaches"""
        results = []
        
        # Approach 1: Try main website with requests
        try:
            print("  Trying main Stonnington website...")
            response = requests.get(
                self.base_url + "/Council/Council-meetings",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for InfoCouncil links or direct PDFs
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    if 'infocouncil' in href.lower() or '.pdf' in href.lower():
                        if any(word in text.lower() for word in ['agenda', 'minutes', 'meeting']):
                            date_str = self.extract_date(text)
                            if date_str:
                                doc_type = self.determine_doc_type(text) or 'agenda'
                                
                                # Fix URL
                                if 'infocouncil' in href and not href.startswith('http'):
                                    href = self.infocouncil_url + href
                                elif not href.startswith('http'):
                                    href = self.base_url + href
                                
                                doc = MeetingDocument(
                                    council_id=self.council_id,
                                    council_name=self.council_name,
                                    document_type=doc_type,
                                    meeting_type='council',
                                    title=text,
                                    date=date_str,
                                    url=href,
                                    webpage_url=response.url
                                )
                                results.append(doc)
        except:
            pass
        
        # Approach 2: Try InfoCouncil directly
        if not results:
            try:
                print("  Trying InfoCouncil directly...")
                
                # Try current year
                year = datetime.now().year
                infocouncil_urls = [
                    f"{self.infocouncil_url}/Open/{year}/",
                    f"{self.infocouncil_url}/",
                    f"{self.infocouncil_url}/Default.aspx"
                ]
                
                for url in infocouncil_urls:
                    try:
                        response = requests.get(url, headers=self.headers, timeout=30)
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.text, 'html.parser')
                            
                            # InfoCouncil table pattern
                            table = soup.find('table', id='grdMenu')
                            if table:
                                rows = table.find_all('tr')
                                for row in rows:
                                    # Find PDF link
                                    pdf_link = row.find('a', class_='bpsGridPDFLink')
                                    if pdf_link:
                                        href = pdf_link.get('href', '')
                                        
                                        # Get date and name from row
                                        date_cell = row.find('td', class_='bpsGridDate')
                                        name_cell = row.find('td', class_='bpsGridCommittee')
                                        
                                        if date_cell:
                                            date_str = self.extract_date(date_cell.get_text(strip=True))
                                            if date_str:
                                                name = name_cell.get_text(strip=True) if name_cell else "Council Meeting"
                                                doc_type = self.determine_doc_type(name) or 'agenda'
                                                
                                                if not href.startswith('http'):
                                                    href = self.infocouncil_url + '/' + href.lstrip('/')
                                                
                                                doc = MeetingDocument(
                                                    council_id=self.council_id,
                                                    council_name=self.council_name,
                                                    document_type=doc_type,
                                                    meeting_type=self.determine_meeting_type(name),
                                                    title=f"{name} - {date_str}",
                                                    date=date_str,
                                                    url=href,
                                                    webpage_url=url
                                                )
                                                results.append(doc)
                            
                            # Also look for any direct links
                            for link in soup.find_all('a', href=lambda x: x and ('.pdf' in x.lower() or 'meeting.aspx' in x.lower())):
                                href = link.get('href', '')
                                text = link.get_text(strip=True)
                                date_str = self.extract_date(text)
                                
                                if date_str and any(word in text.lower() for word in ['agenda', 'minutes']):
                                    doc_type = self.determine_doc_type(text) or 'agenda'
                                    
                                    if not href.startswith('http'):
                                        href = self.infocouncil_url + '/' + href.lstrip('/')
                                    
                                    doc = MeetingDocument(
                                        council_id=self.council_id,
                                        council_name=self.council_name,
                                        document_type=doc_type,
                                        meeting_type='council',
                                        title=text,
                                        date=date_str,
                                        url=href,
                                        webpage_url=url
                                    )
                                    results.append(doc)
                            
                            if results:
                                break
                                
                    except Exception as e:
                        print(f"    Error with {url}: {e}")
                        
            except Exception as e:
                print(f"  InfoCouncil error: {e}")
        
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
