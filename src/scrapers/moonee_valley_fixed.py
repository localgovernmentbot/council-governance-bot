"""
Fixed Moonee Valley scraper for M9 Bot
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime
from dateutil.parser import parse as parse_date
from dataclasses import dataclass
from typing import Optional, List

from m9_adapted import MeetingDocument, BaseM9Scraper


class MooneeValleyFixedScraper(BaseM9Scraper):
    """Fixed Moonee Valley scraper that actually works"""
    
    def __init__(self):
        super().__init__(
            council_id="MOON",
            council_name="Moonee Valley City Council",
            base_url="https://mvcc.vic.gov.au"
        )
    
    def scrape(self):
        """Scrape Moonee Valley using Selenium"""
        results = []
        
        # Setup Chrome
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        
        try:
            driver.get("https://mvcc.vic.gov.au/my-council/council-meetings/")
            time.sleep(3)
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Find first table
            tables = soup.find_all("table")
            if tables:
                tbody = tables[0].find("tbody")
                if tbody:
                    rows = tbody.find_all("tr")
                    
                    # Process each row
                    for row in rows:
                        cells = row.find_all("td")
                        if len(cells) >= 2:
                            # Date/time in first cell
                            date_text = cells[0].text.strip()
                            
                            # Agenda in second cell
                            agenda_cell = cells[1]
                            agenda_link = agenda_cell.find("a")
                            
                            if agenda_link and date_text:
                                href = agenda_link.get('href')
                                
                                # Extract date
                                date_match = re.search(r'(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)', date_text)
                                if date_match:
                                    try:
                                        # Add current year if not specified
                                        date_str = date_match.group()
                                        if '2025' not in date_text and '2024' not in date_text:
                                            date_str += ' 2025'
                                        
                                        parsed_date = parse_date(date_str)
                                        formatted_date = parsed_date.strftime('%Y-%m-%d')
                                        
                                        # Add agenda
                                        doc = MeetingDocument(
                                            council_id=self.council_id,
                                            council_name=self.council_name,
                                            document_type='agenda',
                                            meeting_type='council',
                                            title=f"Council Meeting Agenda - {formatted_date}",
                                            date=formatted_date,
                                            url=href,
                                            webpage_url="https://mvcc.vic.gov.au/my-council/council-meetings/"
                                        )
                                        results.append(doc)
                                    except:
                                        pass
                            
                            # Check for minutes in third cell if exists
                            if len(cells) > 2:
                                minutes_cell = cells[2]
                                minutes_link = minutes_cell.find("a")
                                if minutes_link and results:  # Use date from last agenda
                                    href = minutes_link.get('href')
                                    
                                    doc = MeetingDocument(
                                        council_id=self.council_id,
                                        council_name=self.council_name,
                                        document_type='minutes',
                                        meeting_type='council',
                                        title=f"Council Meeting Minutes - {results[-1].date}",
                                        date=results[-1].date,
                                        url=href,
                                        webpage_url="https://mvcc.vic.gov.au/my-council/council-meetings/"
                                    )
                                    results.append(doc)
        finally:
            driver.quit()
        
        # Sort by date (newest first)
        results.sort(key=lambda x: x.date, reverse=True)
        
        return results
