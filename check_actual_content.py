#!/usr/bin/env python3
"""
Test what's actually on the problematic council pages
Using YIMBY's approach of finding specific elements
"""

import sys
sys.path.append('src/scrapers')

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

print("Checking actual content on M9 council pages")
print("=" * 60)

# Setup Chrome
options = Options()
options.add_argument('--headless')  # Use headless like YIMBY
driver = webdriver.Chrome(options=options)

try:
    # 1. Moonee Valley - Check the table structure
    print("\n1. MOONEE VALLEY")
    print("-" * 30)
    driver.get("https://mvcc.vic.gov.au/my-council/council-meetings/")
    time.sleep(3)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Find table like YIMBY does
    tables = soup.find_all("table")
    print(f"Tables found: {len(tables)}")
    
    if tables:
        tbody = tables[0].find("tbody")
        if tbody:
            rows = tbody.find_all("tr")
            print(f"Rows in table: {len(rows)}")
            
            # Check last row with agenda (YIMBY's approach)
            for i in range(len(rows)-1, -1, -1):
                row = rows[i]
                cells = row.find_all("td")
                if len(cells) >= 2:
                    agenda_cell = cells[1]  # column-2
                    if agenda_cell.text.strip():  # Has content
                        print(f"\nLast row with agenda (row {i}):")
                        print(f"  Date cell: {cells[0].text.strip()}")
                        print(f"  Agenda cell: {agenda_cell.text.strip()}")
                        
                        # Check for link
                        link = agenda_cell.find("a")
                        if link:
                            print(f"  Link found: {link.get('href')}")
                        break
    
    # 2. Yarra - Check page structure
    print("\n\n2. YARRA")
    print("-" * 30)
    driver.get("https://www.yarracity.vic.gov.au/about-us/council-and-committee-meetings")
    time.sleep(3)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Look for any PDF links or meeting links
    pdf_links = soup.find_all('a', href=lambda x: x and '.pdf' in str(x).lower())
    print(f"PDF links: {len(pdf_links)}")
    
    # Check for specific divs or sections
    meeting_divs = soup.find_all("div", class_=lambda x: x and any(cls in str(x).lower() for cls in ['meeting', 'agenda', 'minutes']))
    print(f"Meeting-related divs: {len(meeting_divs)}")
    
    # Check for any links with agenda/minutes text
    agenda_links = soup.find_all('a', text=lambda x: x and any(word in str(x).lower() for word in ['agenda', 'minutes']))
    print(f"Agenda/minutes links: {len(agenda_links)}")
    for link in agenda_links[:3]:
        print(f"  - {link.get_text(strip=True)}")
        print(f"    {link.get('href')}")
    
    # 3. Port Phillip - Quick check
    print("\n\n3. PORT PHILLIP")
    print("-" * 30)
    driver.set_page_load_timeout(30)
    try:
        driver.get("https://www.portphillip.vic.gov.au/about-the-council/meetings-and-minutes")
        time.sleep(5)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        pdf_links = soup.find_all('a', href=lambda x: x and '.pdf' in str(x).lower())
        print(f"PDF links: {len(pdf_links)}")
        
        # Show first few PDFs
        for link in pdf_links[:3]:
            print(f"  - {link.get_text(strip=True)}")
            
    except Exception as e:
        print(f"Error loading Port Phillip: {e}")
    
    # 4. Stonnington - Check main site
    print("\n\n4. STONNINGTON")
    print("-" * 30)
    driver.get("https://www.stonnington.vic.gov.au/Council/Council-meetings")
    time.sleep(3)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Look for links to InfoCouncil or PDFs
    all_links = soup.find_all('a', href=True)
    infocouncil_links = [l for l in all_links if 'infocouncil' in l.get('href', '').lower()]
    pdf_links = [l for l in all_links if '.pdf' in l.get('href', '').lower()]
    
    print(f"InfoCouncil links: {len(infocouncil_links)}")
    print(f"PDF links: {len(pdf_links)}")
    
    if infocouncil_links:
        print("\nInfoCouncil links found:")
        for link in infocouncil_links[:3]:
            print(f"  - {link.get_text(strip=True)}")
            print(f"    {link.get('href')}")
            
finally:
    driver.quit()

print("\n\nAnalysis complete.")
