"""
Yarra City Council scraper using undetected-chromedriver to bypass 403 blocks
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from datetime import datetime
from base_m9 import MeetingDocument, BaseM9Scraper


class YarraUndetectedScraper(BaseM9Scraper):
    """Yarra scraper using undetected ChromeDriver to bypass blocks"""
    
    def __init__(self):
        super().__init__(
            council_id="YARR",
            council_name="Yarra City Council",
            base_url="https://www.yarracity.vic.gov.au"
        )
        
    def setup_driver(self):
        """Setup undetected Chrome driver with anti-detection measures"""
        options = uc.ChromeOptions()
        
        # Add stealth options
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        
        # Random window size to appear more human
        window_sizes = [(1920, 1080), (1366, 768), (1440, 900)]
        width, height = random.choice(window_sizes)
        options.add_argument(f'--window-size={width},{height}')
        
        # Randomize user agent
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        ]
        options.add_argument(f'user-agent={random.choice(user_agents)}')
        
        # Use undetected ChromeDriver
        driver = uc.Chrome(options=options, version_main=None)
        
        # Additional evasion techniques
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": driver.execute_script("return navigator.userAgent").replace("Headless", "")
        })
        
        return driver
    
    def human_like_delay(self, min_seconds=1, max_seconds=3):
        """Add random human-like delay"""
        time.sleep(random.uniform(min_seconds, max_seconds))
    
    def scrape(self):
        """Scrape Yarra using undetected browser"""
        results = []
        driver = None
        
        try:
            driver = self.setup_driver()
            
            # Navigate to main page
            url = "https://www.yarracity.vic.gov.au/about-us/council-and-committee-meetings"
            driver.get(url)
            
            # Wait for page to load with human-like delay
            self.human_like_delay(2, 4)
            
            # Random scroll to simulate human behavior
            driver.execute_script(f"window.scrollTo(0, {random.randint(100, 500)});")
            self.human_like_delay()
            
            # Wait for content to load
            wait = WebDriverWait(driver, 20)
            
            # Look for meeting links or documents
            # Strategy 1: Find links with meeting dates
            meeting_patterns = [
                "//a[contains(@href, '/council-meeting-')]",
                "//a[contains(@href, '.pdf')]",
                "//a[contains(text(), '2025')]",
                "//a[contains(text(), '2024')]"
            ]
            
            found_links = []
            for pattern in meeting_patterns:
                try:
                    elements = driver.find_elements(By.XPATH, pattern)
                    for elem in elements:
                        href = elem.get_attribute('href')
                        text = elem.text.strip()
                        if href and href not in [link[0] for link in found_links]:
                            found_links.append((href, text))
                except:
                    pass
            
            # Process found links
            for href, text in found_links:
                # Check if it's a direct PDF
                if '.pdf' in href.lower():
                    date_str = self.extract_date(text)
                    if date_str:
                        doc_type = 'minutes' if 'minutes' in text.lower() else 'agenda'
                        
                        doc = MeetingDocument(
                            council_id=self.council_id,
                            council_name=self.council_name,
                            document_type=doc_type,
                            meeting_type='council',
                            title=text or f"Council Meeting {doc_type.title()}",
                            date=date_str,
                            url=href,
                            webpage_url=url
                        )
                        results.append(doc)
                
                # Check if it's a meeting page link
                elif '/council-meeting-' in href:
                    # Visit the meeting page
                    try:
                        driver.get(href)
                        self.human_like_delay(1, 2)
                        
                        # Look for PDFs on the page
                        pdf_links = driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
                        
                        for pdf_link in pdf_links:
                            pdf_href = pdf_link.get_attribute('href')
                            pdf_text = pdf_link.text.strip()
                            
                            if pdf_href:
                                date_str = self.extract_date(pdf_text) or self.extract_date(href)
                                if date_str:
                                    doc_type = 'minutes' if 'minutes' in pdf_text.lower() else 'agenda'
                                    
                                    doc = MeetingDocument(
                                        council_id=self.council_id,
                                        council_name=self.council_name,
                                        document_type=doc_type,
                                        meeting_type='council',
                                        title=pdf_text or f"Council Meeting {doc_type.title()}",
                                        date=date_str,
                                        url=pdf_href,
                                        webpage_url=href
                                    )
                                    results.append(doc)
                        
                        # Go back to main page
                        driver.back()
                        self.human_like_delay()
                        
                    except Exception as e:
                        print(f"  Error visiting meeting page: {e}")
            
            # Strategy 2: Check for direct file paths pattern
            # Yarra uses /sites/default/files/ pattern
            file_pattern_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/sites/default/files/')]")
            
            for link in file_pattern_links:
                href = link.get_attribute('href')
                text = link.text.strip()
                
                if href and '.pdf' in href.lower():
                    date_str = self.extract_date(text)
                    if date_str:
                        doc_type = 'minutes' if 'minutes' in href.lower() else 'agenda'
                        
                        doc = MeetingDocument(
                            council_id=self.council_id,
                            council_name=self.council_name,
                            document_type=doc_type,
                            meeting_type='council',
                            title=text or f"Council Meeting {doc_type.title()}",
                            date=date_str,
                            url=href,
                            webpage_url=driver.current_url
                        )
                        results.append(doc)
            
        except Exception as e:
            print(f"  Error with undetected scraper: {e}")
            
        finally:
            if driver:
                driver.quit()
        
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


# Fallback scraper using requests-html for JavaScript rendering
class YarraJSScraper(BaseM9Scraper):
    """Alternative Yarra scraper using requests-html for JS rendering"""
    
    def __init__(self):
        super().__init__(
            council_id="YARR",
            council_name="Yarra City Council",
            base_url="https://www.yarracity.vic.gov.au"
        )
    
    def scrape(self):
        """Scrape using requests-html with JS rendering"""
        from requests_html import HTMLSession
        
        results = []
        session = HTMLSession()
        
        try:
            # Use JS rendering
            url = "https://www.yarracity.vic.gov.au/about-us/council-and-committee-meetings"
            
            # Add headers to avoid blocks
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            }
            
            r = session.get(url, headers=headers)
            
            # Render JavaScript
            r.html.render(timeout=20, wait=2)
            
            # Find all PDF links
            pdf_links = r.html.find('a')
            
            for link in pdf_links:
                href = link.attrs.get('href', '')
                text = link.text
                
                if '.pdf' in href.lower():
                    date_str = self.extract_date(text)
                    if date_str:
                        doc_type = 'minutes' if 'minutes' in text.lower() else 'agenda'
                        
                        if not href.startswith('http'):
                            href = self.base_url + href
                        
                        doc = MeetingDocument(
                            council_id=self.council_id,
                            council_name=self.council_name,
                            document_type=doc_type,
                            meeting_type='council',
                            title=text or f"Council Meeting {doc_type.title()}",
                            date=date_str,
                            url=href,
                            webpage_url=url
                        )
                        results.append(doc)
                        
        except Exception as e:
            print(f"  Error with JS rendering: {e}")
        finally:
            session.close()
        
        return results


if __name__ == "__main__":
    print("Testing Yarra City Council Scrapers")
    print("=" * 60)
    
    # Try undetected scraper first
    print("\n1. Testing Undetected ChromeDriver approach:")
    try:
        scraper = YarraUndetectedScraper()
        docs = scraper.scrape()
        print(f"  Found {len(docs)} documents")
        if docs:
            for doc in docs[:3]:
                print(f"  - {doc.date}: {doc.title[:50]}...")
    except Exception as e:
        print(f"  Failed: {e}")
        
    # Try JS rendering approach
    print("\n2. Testing requests-html JS rendering approach:")
    try:
        scraper = YarraJSScraper()
        docs = scraper.scrape()
        print(f"  Found {len(docs)} documents")
        if docs:
            for doc in docs[:3]:
                print(f"  - {doc.date}: {doc.title[:50]}...")
    except Exception as e:
        print(f"  Failed: {e}")
