#!/usr/bin/env python3
"""
Detailed debugging for Yarra and Stonnington - check what's actually on their websites
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

print("=" * 60)
print("DETAILED COUNCIL WEBSITE DEBUGGING")
print("=" * 60)

def check_url_exists(url):
    """Check if URL exists and what type it is"""
    try:
        response = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
        content_type = response.headers.get('Content-Type', '').lower()
        return response.status_code, content_type
    except Exception as e:
        return None, str(e)

# 1. Check Yarra's actual website
print("\n1. YARRA CITY COUNCIL - Website Analysis")
print("-" * 40)

yarra_urls = [
    "https://www.yarracity.vic.gov.au/about-us/council-meetings",
    "https://www.yarracity.vic.gov.au/about-us/committees-meetings-and-minutes",
    "https://www.yarracity.vic.gov.au/about-us/council-and-committee-meetings/upcoming-council-and-committee-meetings"
]

print("Checking Yarra pages:")
for url in yarra_urls:
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"\n✓ {url}")
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find PDF links
            pdf_links = soup.find_all('a', href=lambda x: x and '.pdf' in x.lower())
            print(f"  PDF links found: {len(pdf_links)}")
            
            if pdf_links:
                print("  Sample PDFs:")
                for link in pdf_links[:5]:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)[:50]
                    print(f"    - {text}: {href[:60]}...")
            
            # Look for meeting-related text
            agenda_mentions = len(soup.find_all(text=re.compile(r'agenda', re.I)))
            minutes_mentions = len(soup.find_all(text=re.compile(r'minutes', re.I)))
            print(f"  'Agenda' mentions: {agenda_mentions}, 'Minutes' mentions: {minutes_mentions}")
            
    except Exception as e:
        print(f"✗ Error accessing {url}: {e}")

# Check some direct Yarra URLs we expect to work
print("\n\nTrying direct Yarra PDF URLs:")
test_urls = [
    # Try September 2024 patterns (check if they're still using this pattern)
    "https://www.yarracity.vic.gov.au/sites/default/files/2024-09/20240910-council-agenda.pdf",
    "https://www.yarracity.vic.gov.au/sites/default/files/2024-08/20240813-council-agenda.pdf",
    "https://www.yarracity.vic.gov.au/sites/default/files/2024-07/20240709-council-agenda.pdf",
]

for url in test_urls:
    status, content_type = check_url_exists(url)
    if status == 200:
        print(f"  ✓ FOUND: {url}")
    else:
        print(f"  ✗ Not found ({status}): {url}")

# 2. Check Stonnington's actual website
print("\n\n2. STONNINGTON CITY COUNCIL - Website Analysis")
print("-" * 40)

stonnington_urls = [
    "https://www.stonnington.vic.gov.au/About/Council-meetings",
    "https://www.stonnington.vic.gov.au/About/Council-meetings/Meeting-agendas-and-minutes",
    "https://www.stonnington.vic.gov.au/Council/Council-meetings"
]

print("Checking Stonnington pages:")
for url in stonnington_urls:
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"\n✓ {url}")
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find PDF links
            pdf_links = soup.find_all('a', href=lambda x: x and '.pdf' in x.lower())
            print(f"  PDF links found: {len(pdf_links)}")
            
            if pdf_links:
                print("  Sample PDFs:")
                for link in pdf_links[:5]:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)[:50]
                    print(f"    - {text}: {href[:60]}...")
            
            # Look for InfoCouncil references
            infocouncil_links = soup.find_all('a', href=lambda x: x and 'infocouncil' in str(x).lower())
            if infocouncil_links:
                print(f"  InfoCouncil links found: {len(infocouncil_links)}")
                for link in infocouncil_links[:3]:
                    print(f"    - {link.get('href', '')}")
            
    except Exception as e:
        print(f"✗ Error accessing {url}: {e}")

# Check InfoCouncil directly
print("\n\nChecking Stonnington InfoCouncil:")
infocouncil_url = "https://stonnington.infocouncil.biz"
try:
    response = requests.get(infocouncil_url, headers=headers, timeout=10)
    print(f"InfoCouncil status: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find meeting links
        meeting_links = soup.find_all('a', href=lambda x: x and ('meeting' in str(x).lower() or '.pdf' in str(x).lower()))
        print(f"Meeting-related links: {len(meeting_links)}")
        
        if meeting_links:
            print("Sample links:")
            for link in meeting_links[:5]:
                href = link.get('href', '')
                text = link.get_text(strip=True)[:50]
                print(f"  - {text}: {href}")
                
except Exception as e:
    print(f"Error accessing InfoCouncil: {e}")

# Try some direct Stonnington URLs
print("\n\nTrying direct Stonnington PDF URLs:")
test_urls = [
    # Recent patterns
    "https://www.stonnington.vic.gov.au/files/assets/public/v/2/about/council-meetings/2024/19-aug-2024/agenda.pdf",
    "https://www.stonnington.vic.gov.au/files/assets/public/v/2/about/council-meetings/2024/05-aug-2024/agenda.pdf",
    "https://stonnington.infocouncil.biz/Open/2024/08/ORD_19082024_AGN_AT.PDF",
]

for url in test_urls:
    status, content_type = check_url_exists(url)
    if status == 200:
        print(f"  ✓ FOUND: {url}")
    else:
        print(f"  ✗ Not found ({status}): {url}")

print("\n" + "=" * 60)
print("DEBUGGING COMPLETE")
print("=" * 60)
print("\nCheck the output above to see:")
print("1. Which pages are accessible")
print("2. What PDF links are actually on the pages")
print("3. Which direct URL patterns work")
