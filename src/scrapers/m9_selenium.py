"""
M9 Council Scrapers - Selenium-based for problematic councils
Using proven methods from GitHub research
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime
from dateutil.parser import parse as parse_date
from dataclasses import dataclass
from typing import Optional, List
import logging

# Import our base classes
from m9_adapted import MeetingDocument, BaseM9Scraper


class SeleniumM9Scraper(BaseM9Scraper):
    """Base class for Selenium-based M9 scrapers"""
    
    def __init__(self, council_id: str, council_name: str, base_url: str):
        super().__init__(council_id, council_name, base_url)
        self.driver = None
        
    def setup_driver(self, use_undetected=True):
        """Setup Selenium driver with anti-detection measures"""
        if use_undetected:
            # Use undetected-chromedriver for Cloudflare bypass
            options = uc.ChromeOptions()
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Headless can be detected, so avoid if possible
            # options.add_argument('--headless')
            
            self.driver = uc.Chrome(options=options)
        else:
            # Standard Chrome driver
            options = Options()
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--disable-blink-features=AutomationControlled')
            
            self.driver = webdriver.Chrome(options=options)
    
    def close_driver(self):
        """Close the Selenium driver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def wait_for_element(self, selector, by=By.CSS_SELECTOR, timeout=10):
        """Wait for element to be present"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            return element
        except:
            return None
    
    def get_page_source(self, url):
        """Get page source using Selenium"""
        try:
            self.driver.get(url)
            # Wait for page to load
            time.sleep(3)
            # Additional wait for dynamic content
            self.wait_for_element('body')
            return self.driver.page_source
        except Exception as e:
            print(f"Error loading {url}: {e}")
            return ""


class YarraSeleniumScraper(SeleniumM9Scraper):
    """Yarra scraper using Selenium to bypass 403 Forbidden"""
    
    def __init__(self):
        super().__init__(
            council_id="YARR",
            council_name="Yarra City Council",
            base_url="https://www.yarracity.vic.gov.au"
        )
    
    def scrape(self):
        """Scrape Yarra using Selenium"""
        results = []
        
        # Setup driver with undetected chrome
        self.setup_driver(use_undetected=True)
        
        try:
            # Try upcoming meetings page
            url = "https://www.yarracity.vic.gov.au/about-us/council-and-committee-meetings/upcoming-council-and-committee-meetings"
            print(f"  Loading Yarra page with Selenium...")
            
            html = self.get_page_source(url)
            
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                
                # Look for meeting sections
                meeting_divs = soup.find_all("div", class_=["show-for-medium-up", "card", "meeting"])
                
                for div in meeting_divs:
                    # Find all links in the div
                    for link in div.find_all("a", href=True):
                        href = link.get('href', '')
                        text = link.get_text(strip=True)
                        
                        # Check if it's a document link
                        if any(word in text.lower() for word in ['agenda', 'minutes']):
                            # Determine document type
                            doc_type = self.determine_doc_type(text)
                            if not doc_type:
                                continue
                            
                            # Extract date
                            date_str = self.extract_date(text)
                            if not date_str:
                                # Look in parent elements
                                parent_text = div.get_text(strip=True)
                                date_str = self.extract_date(parent_text)
                            
                            if not date_str:
                                continue
                            
                            # Make URL absolute
                            if not href.startswith('http'):
                                href = self.base_url + href
                            
                            # Determine meeting type
                            meeting_type = self.determine_meeting_type(text)
                            
                            # Create document
                            doc = MeetingDocument(
                                council_id=self.council_id,
                                council_name=self.council_name,
                                document_type=doc_type,
                                meeting_type=meeting_type,
                                title=text,
                                date=date_str,
                                url=href,
                                webpage_url=url
                            )
                            
                            results.append(doc)
                
                # Also check past meetings
                past_url = "https://www.yarracity.vic.gov.au/about-us/council-and-committee-meetings"
                html = self.get_page_source(past_url)
                
                if html:
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Look for PDF links
                    for link in soup.find_all('a', href=lambda x: x and '.pdf' in x.lower()):
                        href = link.get('href', '')
                        text = link.get_text(strip=True)
                        
                        doc_type = self.determine_doc_type(text)
                        if not doc_type:
                            continue
                        
                        date_str = self.extract_date(text)
                        if not date_str:
                            continue
                        
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
                            webpage_url=past_url
                        )
                        
                        results.append(doc)
                        
        finally:
            self.close_driver()
        
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


class MooneeValleySeleniumScraper(SeleniumM9Scraper):
    """Moonee Valley scraper using Selenium for dynamic content"""
    
    def __init__(self):
        super().__init__(
            council_id="MOON",
            council_name="Moonee Valley City Council",
            base_url="https://mvcc.vic.gov.au"
        )
    
    def scrape(self):
        """Scrape Moonee Valley using Selenium"""
        results = []
        
        # Setup driver
        self.setup_driver(use_undetected=False)  # Try standard first
        
        try:
            url = "https://mvcc.vic.gov.au/my-council/council-meetings/"
            print(f"  Loading Moonee Valley page with Selenium...")
            
            self.driver.get(url)
            time.sleep(5)  # Wait for JavaScript to load
            
            # Look for table
            try:
                table = self.driver.find_element(By.TAG_NAME, "table")
                tbody = table.find_element(By.TAG_NAME, "tbody")
                rows = tbody.find_elements(By.TAG_NAME, "tr")
                
                print(f"    Found {len(rows)} table rows")
                
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 2:
                        # Column 1: Date/time
                        datetime_text = cells[0].text.strip()
                        date_str = self.extract_date(datetime_text)
                        
                        if not date_str:
                            continue
                        
                        # Column 2: Agenda
                        agenda_links = cells[1].find_elements(By.TAG_NAME, "a")
                        for link in agenda_links:
                            href = link.get_attribute("href")
                            if href:
                                doc = MeetingDocument(
                                    council_id=self.council_id,
                                    council_name=self.council_name,
                                    document_type='agenda',
                                    meeting_type='council',
                                    title=f"Council Meeting Agenda - {date_str}",
                                    date=date_str,
                                    url=href,
                                    webpage_url=url
                                )
                                results.append(doc)
                        
                        # Column 3: Minutes (if exists)
                        if len(cells) > 2:
                            minutes_links = cells[2].find_elements(By.TAG_NAME, "a")
                            for link in minutes_links:
                                href = link.get_attribute("href")
                                if href:
                                    doc = MeetingDocument(
                                        council_id=self.council_id,
                                        council_name=self.council_name,
                                        document_type='minutes',
                                        meeting_type='council',
                                        title=f"Council Meeting Minutes - {date_str}",
                                        date=date_str,
                                        url=href,
                                        webpage_url=url
                                    )
                                    results.append(doc)
                                    
            except Exception as e:
                print(f"    Error finding table: {e}")
                
                # Fallback: get page source and parse
                html = self.driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                
                # Look for any PDF links
                for link in soup.find_all('a', href=lambda x: x and '.pdf' in x.lower()):
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    doc_type = self.determine_doc_type(text)
                    if not doc_type:
                        continue
                    
                    date_str = self.extract_date(text)
                    if not date_str:
                        continue
                    
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
                        webpage_url=url
                    )
                    
                    results.append(doc)
                    
        finally:
            self.close_driver()
        
        # Sort by date
        results.sort(key=lambda x: x.date, reverse=True)
        
        return results


class PortPhillipSeleniumScraper(SeleniumM9Scraper):
    """Port Phillip scraper using Selenium for slow site"""
    
    def __init__(self):
        super().__init__(
            council_id="PORT",
            council_name="Port Phillip City Council",
            base_url="https://www.portphillip.vic.gov.au"
        )
    
    def scrape(self):
        """Scrape Port Phillip using Selenium with longer timeout"""
        results = []
        
        # Setup driver
        self.setup_driver(use_undetected=False)
        
        try:
            url = "https://www.portphillip.vic.gov.au/about-the-council/meetings-and-minutes"
            print(f"  Loading Port Phillip page with Selenium (may be slow)...")
            
            # Set longer timeout
            self.driver.set_page_load_timeout(60)
            
            try:
                self.driver.get(url)
                time.sleep(10)  # Extra wait for slow site
                
                html = self.driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                
                # Look for PDF links
                for link in soup.find_all('a', href=lambda x: x and '.pdf' in x.lower()):
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    doc_type = self.determine_doc_type(text)
                    if not doc_type:
                        continue
                    
                    date_str = self.extract_date(text)
                    if not date_str:
                        continue
                    
                    if not href.startswith('http'):
                        href = self.base_url + href
                    
                    meeting_type = self.determine_meeting_type(text)
                    
                    doc = MeetingDocument(
                        council_id=self.council_id,
                        council_name=self.council_name,
                        document_type=doc_type,
                        meeting_type=meeting_type,
                        title=text,
                        date=date_str,
                        url=href,
                        webpage_url=url
                    )
                    
                    results.append(doc)
                    
            except Exception as e:
                print(f"    Error loading page: {e}")
                
        finally:
            self.close_driver()
        
        # Sort by date
        results.sort(key=lambda x: x.date, reverse=True)
        
        return results


class StonningtonSeleniumScraper(SeleniumM9Scraper):
    """Stonnington scraper using Selenium for InfoCouncil"""
    
    def __init__(self):
        super().__init__(
            council_id="STON",
            council_name="Stonnington City Council",
            base_url="https://www.stonnington.vic.gov.au"
        )
    
    def scrape(self):
        """Scrape Stonnington using Selenium"""
        results = []
        
        # Setup driver
        self.setup_driver(use_undetected=False)
        
        try:
            # Try main council website first
            url = "https://www.stonnington.vic.gov.au/Council/Council-meetings/Meeting-agendas-and-minutes"
            print(f"  Loading Stonnington page with Selenium...")
            
            html = self.get_page_source(url)
            
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                
                # Look for meeting links or PDFs
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    # Check if it's a meeting document
                    if any(word in text.lower() for word in ['agenda', 'minutes']) or '.pdf' in href.lower():
                        doc_type = self.determine_doc_type(text)
                        if not doc_type:
                            continue
                        
                        date_str = self.extract_date(text)
                        if not date_str:
                            continue
                        
                        # Handle various URL formats
                        if 'infocouncil' in href:
                            # InfoCouncil link
                            if not href.startswith('http'):
                                href = 'https://stonnington.infocouncil.biz' + href
                        elif not href.startswith('http'):
                            href = self.base_url + href
                        
                        meeting_type = self.determine_meeting_type(text)
                        
                        doc = MeetingDocument(
                            council_id=self.council_id,
                            council_name=self.council_name,
                            document_type=doc_type,
                            meeting_type=meeting_type,
                            title=text,
                            date=date_str,
                            url=href,
                            webpage_url=url
                        )
                        
                        results.append(doc)
                
                # If no results, try InfoCouncil directly
                if not results:
                    print("    No results from main site, trying InfoCouncil...")
                    
                    info_url = "https://stonnington.infocouncil.biz"
                    html = self.get_page_source(info_url)
                    
                    if html:
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # InfoCouncil pattern
                        for link in soup.find_all('a', href=True):
                            href = link.get('href', '')
                            text = link.get_text(strip=True)
                            
                            if any(pattern in href.lower() for pattern in ['meeting.aspx', 'download.aspx', '.pdf']):
                                if any(word in text.lower() for word in ['agenda', 'minutes']):
                                    doc_type = self.determine_doc_type(text)
                                    if not doc_type:
                                        continue
                                    
                                    date_str = self.extract_date(text)
                                    if not date_str:
                                        continue
                                    
                                    if not href.startswith('http'):
                                        href = 'https://stonnington.infocouncil.biz' + ('/' + href if not href.startswith('/') else href)
                                    
                                    doc = MeetingDocument(
                                        council_id=self.council_id,
                                        council_name=self.council_name,
                                        document_type=doc_type,
                                        meeting_type='council',
                                        title=text,
                                        date=date_str,
                                        url=href,
                                        webpage_url=info_url
                                    )
                                    
                                    results.append(doc)
                                    
        finally:
            self.close_driver()
        
        # Sort by date
        results.sort(key=lambda x: x.date, reverse=True)
        
        return results
