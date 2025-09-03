#!/usr/bin/env python3
"""
Debug Selenium scrapers to see what's happening
"""

import sys
sys.path.append('src/scrapers')

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

print("Debugging M9 Selenium Scrapers")
print("=" * 60)

# Setup Chrome
options = Options()
options.add_argument('--disable-blink-features=AutomationControlled')
driver = webdriver.Chrome(options=options)

try:
    # Test Moonee Valley since it found 14 rows
    print("\n1. MOONEE VALLEY - Checking table content...")
    driver.get("https://mvcc.vic.gov.au/my-council/council-meetings/")
    time.sleep(5)
    
    # Look for table
    try:
        table = driver.find_element(By.TAG_NAME, "table")
        tbody = table.find_element(By.TAG_NAME, "tbody")
        rows = tbody.find_elements(By.TAG_NAME, "tr")
        
        print(f"Found {len(rows)} rows")
        
        # Check first few rows
        for i, row in enumerate(rows[:3]):
            print(f"\nRow {i+1}:")
            cells = row.find_elements(By.TAG_NAME, "td")
            for j, cell in enumerate(cells):
                print(f"  Cell {j+1}: {cell.text}")
                # Check for links
                links = cell.find_elements(By.TAG_NAME, "a")
                for link in links:
                    print(f"    Link: {link.get_attribute('href')}")
                    
    except Exception as e:
        print(f"Error finding table: {e}")
        
    # Check page source
    print("\n2. Checking page source for PDFs...")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    pdf_links = soup.find_all('a', href=lambda x: x and '.pdf' in str(x).lower())
    print(f"PDF links in page: {len(pdf_links)}")
    
    # Test Yarra
    print("\n3. YARRA - Checking what's on the page...")
    driver.get("https://www.yarracity.vic.gov.au/about-us/council-and-committee-meetings/upcoming-council-and-committee-meetings")
    time.sleep(5)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Look for any links with meeting keywords
    meeting_links = []
    for link in soup.find_all('a', href=True):
        text = link.get_text(strip=True)
        if any(word in text.lower() for word in ['agenda', 'minutes', 'meeting']):
            meeting_links.append({
                'text': text,
                'href': link['href']
            })
    
    print(f"Meeting-related links found: {len(meeting_links)}")
    for ml in meeting_links[:5]:
        print(f"  - {ml['text']}")
        print(f"    {ml['href']}")
        
finally:
    driver.quit()

print("\nDebug complete.")
