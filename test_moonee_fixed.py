#!/usr/bin/env python3
"""
Fixed Moonee Valley scraper based on actual page structure
"""

import sys
sys.path.append('src/scrapers')

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import re
from dateutil.parser import parse as parse_date

print("Testing fixed Moonee Valley scraper")
print("=" * 40)

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
            
            documents = []
            
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
                                
                                documents.append({
                                    'date': parsed_date.strftime('%Y-%m-%d'),
                                    'text': date_text,
                                    'type': 'agenda',
                                    'url': href
                                })
                            except:
                                pass
                    
                    # Check for minutes in third cell if exists
                    if len(cells) > 2:
                        minutes_cell = cells[2]
                        minutes_link = minutes_cell.find("a")
                        if minutes_link:
                            href = minutes_link.get('href')
                            documents.append({
                                'date': documents[-1]['date'] if documents else '',
                                'text': date_text,
                                'type': 'minutes',
                                'url': href
                            })
            
            print(f"Found {len(documents)} documents:")
            for doc in documents:
                print(f"\n{doc['date']} - {doc['type'].title()}")
                print(f"  URL: {doc['url']}")
                
finally:
    driver.quit()
