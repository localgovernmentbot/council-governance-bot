#!/usr/bin/env python3
"""
Debug URL patterns directly with verbose output
"""

import requests
from datetime import datetime, timedelta

print("=" * 60)
print("DIRECT URL DEBUGGING")
print("=" * 60)

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def test_url_verbose(url):
    """Test URL with detailed output"""
    print(f"\nTesting: {url}")
    try:
        response = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
        print(f"  Status: {response.status_code}")
        print(f"  Content-Type: {response.headers.get('Content-Type', 'Not specified')}")
        print(f"  Final URL: {response.url}")
        
        if response.status_code == 200:
            if 'pdf' in response.headers.get('Content-Type', '').lower():
                print("  ✅ Valid PDF found!")
                return True
            else:
                print("  ⚠️ Found but not a PDF")
        else:
            print("  ❌ Not found")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

# First, let's check what dates we should be looking for
print("\n1. EXPECTED MEETING DATES (last 2 months)")
print("-" * 40)

current = datetime.now()
print(f"Current date: {current.strftime('%Y-%m-%d')}")
print("\nTypical meeting dates (Tuesdays):")

for weeks_back in range(8):
    date = current - timedelta(weeks=weeks_back)
    # Find Tuesday
    days_until_tuesday = (1 - date.weekday()) % 7
    tuesday = date + timedelta(days=days_until_tuesday) if days_until_tuesday else date
    
    if tuesday <= current:
        print(f"  {tuesday.strftime('%Y-%m-%d')} ({tuesday.strftime('%B %d')})")

# Test Yarra patterns
print("\n2. YARRA CITY COUNCIL TESTS")
print("-" * 40)

# Let's try some specific recent dates we know might exist
yarra_test_urls = [
    # August 2024 (last month)
    "https://www.yarracity.vic.gov.au/sites/default/files/2024-08/20240813-council-agenda.pdf",
    "https://www.yarracity.vic.gov.au/sites/default/files/2024-08/20240813-council-minutes.pdf",
    "https://www.yarracity.vic.gov.au/sites/default/files/2024-08/20240827-council-agenda.pdf",
    
    # July 2024
    "https://www.yarracity.vic.gov.au/sites/default/files/2024-07/20240709-council-agenda.pdf",
    "https://www.yarracity.vic.gov.au/sites/default/files/2024-07/20240723-council-agenda.pdf",
    
    # Try alternative patterns
    "https://www.yarracity.vic.gov.au/sites/default/files/2024-08/council-meeting-agenda-13-august-2024.pdf",
]

yarra_found = []
for url in yarra_test_urls:
    if test_url_verbose(url):
        yarra_found.append(url)

# Test Stonnington patterns
print("\n3. STONNINGTON CITY COUNCIL TESTS")
print("-" * 40)

# Test recent Stonnington URLs
stonnington_test_urls = [
    # Try August 2024
    "https://www.stonnington.vic.gov.au/files/assets/public/v/2/about/council-meetings/2024/20-aug-2024/agenda.pdf",
    "https://www.stonnington.vic.gov.au/files/assets/public/v/2/about/council-meetings/2024/20-august-2024/agenda.pdf",
    
    # Try July 2024
    "https://www.stonnington.vic.gov.au/files/assets/public/v/2/about/council-meetings/2024/16-jul-2024/agenda.pdf",
    "https://www.stonnington.vic.gov.au/files/assets/public/v/2/about/council-meetings/2024/16-july-2024/agenda.pdf",
]

ston_found = []
for url in stonnington_test_urls:
    if test_url_verbose(url):
        ston_found.append(url)

# Try InfoCouncil for Stonnington
print("\n4. STONNINGTON INFOCOUNCIL TESTS")
print("-" * 40)

infocouncil_urls = [
    # August 2024
    "https://stonnington.infocouncil.biz/Open/2024/08/ORD_20082024_AGN_AT.PDF",
    "https://stonnington.infocouncil.biz/Open/2024/08/ORD_20082024_MIN.PDF",
    
    # July 2024
    "https://stonnington.infocouncil.biz/Open/2024/07/ORD_16072024_AGN_AT.PDF",
]

info_found = []
for url in infocouncil_urls:
    if test_url_verbose(url):
        info_found.append(url)

# Summary
print("\n" + "=" * 60)
print("DEBUGGING RESULTS")
print("=" * 60)

if yarra_found:
    print(f"\n✅ Yarra: Found {len(yarra_found)} working URLs")
    print("Working pattern examples:")
    for url in yarra_found[:2]:
        print(f"  - {url}")
else:
    print("\n❌ Yarra: No working URLs found")

if ston_found or info_found:
    print(f"\n✅ Stonnington: Found {len(ston_found) + len(info_found)} working URLs")
    if ston_found:
        print("Main site pattern:")
        print(f"  - {ston_found[0]}")
    if info_found:
        print("InfoCouncil pattern:")
        print(f"  - {info_found[0]}")
else:
    print("\n❌ Stonnington: No working URLs found")

print("\nNOTE: We're testing 2024 dates (not 2025) since we're in September 2024")
print("The scrapers may need to be adjusted to look at correct date ranges.")
