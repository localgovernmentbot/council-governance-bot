#!/usr/bin/env python3
"""
Debug: Check meeting dates and publication timing
"""

from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

print("Council Meeting Publication Timing Analysis")
print("=" * 50)
print(f"Today: Tuesday, September 2, 2025")
print(f"Next meeting likely: Tuesday, September 9, 2025")
print(f"Agenda publication: Friday, September 5, 2025")
print()

# Calculate dates
today = datetime(2025, 9, 2)  # Tuesday
next_tuesday = today + timedelta(days=7)
this_friday = today + timedelta(days=3)
last_friday = today - timedelta(days=4)

print(f"Key dates:")
print(f"- Last Friday: {last_friday.strftime('%B %d, %Y')}")
print(f"- Today: {today.strftime('%B %d, %Y')}")
print(f"- This Friday: {this_friday.strftime('%B %d, %Y')}")
print(f"- Next Tuesday: {next_tuesday.strftime('%B %d, %Y')}")
print()

print("INSIGHT: We should be looking for:")
print("1. PAST meetings (already happened) - these will have minutes")
print("2. TODAY'S meeting (Sept 2) - agenda should be available")
print("3. NEXT meeting (Sept 9) - agenda not yet published")
print()

# Check what Moonee Valley has (we know it works)
print("Checking Moonee Valley dates...")
url = "https://mvcc.vic.gov.au/my-council/council-meetings/"

try:
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find first table
        tables = soup.find_all("table")
        if tables:
            tbody = tables[0].find("tbody")
            if tbody:
                rows = tbody.find_all("tr")[:5]  # First 5 rows
                
                print("\nMoonee Valley upcoming meetings:")
                for row in rows:
                    cells = row.find_all("td")
                    if cells:
                        date_text = cells[0].text.strip()
                        print(f"  - {date_text}")
                        
except Exception as e:
    print(f"Error: {e}")

print("\nCONCLUSION:")
print("The 3 'failing' councils might actually be working correctly.")
print("They just don't have future meetings published yet!")
print("We should check for PAST meetings instead.")
