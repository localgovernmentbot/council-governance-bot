#!/usr/bin/env python3
"""
Direct URL testing for Yarra and Stonnington patterns
"""

import requests
from datetime import datetime, timedelta

print("=" * 60)
print("TESTING COUNCIL URL PATTERNS DIRECTLY")
print("=" * 60)

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

def test_url(url, council_name):
    """Test if a URL exists and is a PDF"""
    try:
        # Use HEAD request to check without downloading
        response = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
        content_type = response.headers.get('Content-Type', '').lower()
        
        if response.status_code == 200:
            if 'pdf' in content_type:
                print(f"✅ {council_name}: FOUND PDF at {url}")
                return True
            else:
                print(f"⚠️  {council_name}: Found but not PDF (type: {content_type})")
                return False
        else:
            print(f"❌ {council_name}: Not found (status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ {council_name}: Error - {str(e)[:50]}")
        return False

# Test Yarra patterns
print("\n1. YARRA CITY COUNCIL")
print("-" * 40)
print("Testing known URL patterns...")

# Try some recent meeting patterns
yarra_urls = [
    # Try August 2025 patterns
    "https://www.yarracity.vic.gov.au/sites/default/files/2025-08/20250812-council-agenda.pdf",
    "https://www.yarracity.vic.gov.au/sites/default/files/2025-08/20250812_council_agenda.pdf",
    "https://www.yarracity.vic.gov.au/sites/default/files/2025-08/council-meeting-agenda-12-august-2025.pdf",
    
    # Try July 2025 patterns
    "https://www.yarracity.vic.gov.au/sites/default/files/2025-07/20250708-council-agenda.pdf",
    "https://www.yarracity.vic.gov.au/sites/default/files/2025-07/20250708_council_agenda.pdf",
    "https://www.yarracity.vic.gov.au/sites/default/files/2025-07/council-meeting-agenda-8-july-2025.pdf",
    
    # Try June 2025 patterns  
    "https://www.yarracity.vic.gov.au/sites/default/files/2025-06/20250610-council-agenda.pdf",
    "https://www.yarracity.vic.gov.au/sites/default/files/2025-06/20250624-council-minutes.pdf",
]

yarra_found = 0
for url in yarra_urls:
    if test_url(url, "Yarra"):
        yarra_found += 1

print(f"\nYarra Results: {yarra_found}/{len(yarra_urls)} URLs working")

# Test Stonnington patterns
print("\n2. STONNINGTON CITY COUNCIL")
print("-" * 40)
print("Testing known URL patterns...")

stonnington_base = "https://www.stonnington.vic.gov.au/files/assets/public/v/2/about/council-meetings"

# Generate some test dates (Tuesdays/Wednesdays)
test_dates = []
current = datetime.now()

for weeks_back in range(8):
    check_date = current - timedelta(weeks=weeks_back)
    # Find Tuesday of that week
    tuesday = check_date - timedelta(days=(check_date.weekday() - 1) % 7)
    test_dates.append(tuesday)

stonnington_urls = []
for date in test_dates[:4]:  # Test last 4 weeks
    year = date.strftime('%Y')
    dd = date.strftime('%d')
    month_full = date.strftime('%B').lower()
    month_short = date.strftime('%b').lower()
    
    # Try different patterns
    patterns = [
        f"{stonnington_base}/{year}/{dd}-{month_short}-{year}/agenda.pdf",
        f"{stonnington_base}/{year}/{dd}-{month_full}-{year}/agenda.pdf",
        f"{stonnington_base}/{year}/{dd}-{month_short}-{year}/minutes.pdf",
        f"{stonnington_base}/{year}/{dd}-{month_full}-{year}/council-meeting-agenda-{dd}-{month_full}-{year}.pdf",
    ]
    
    stonnington_urls.extend(patterns[:2])  # Test first 2 patterns for each date

ston_found = 0
for url in stonnington_urls:
    if test_url(url, "Stonnington"):
        ston_found += 1

print(f"\nStonnington Results: {ston_found}/{len(stonnington_urls)} URLs working")

# Try InfoCouncil pattern for Stonnington
print("\n3. STONNINGTON INFOCOUNCIL (Alternative)")
print("-" * 40)

infocouncil_urls = [
    "https://stonnington.infocouncil.biz/Open/2025/08/ORD_19082025_AGN_AT.PDF",
    "https://stonnington.infocouncil.biz/Open/2025/07/ORD_22072025_AGN_AT.PDF",
    "https://stonnington.infocouncil.biz/Open/2025/06/ORD_17062025_AGN_AT.PDF",
]

info_found = 0
for url in infocouncil_urls:
    if test_url(url, "Stonnington InfoCouncil"):
        info_found += 1

print(f"\nInfoCouncil Results: {info_found}/{len(infocouncil_urls)} URLs working")

print("\n" + "=" * 60)
print("PATTERN TEST COMPLETE")
print("=" * 60)

if yarra_found > 0:
    print("\n✅ Yarra has working URL patterns - scraper needs adjustment")
else:
    print("\n❌ Yarra patterns not working - may need to check website manually")

if ston_found > 0 or info_found > 0:
    print("✅ Stonnington has working URL patterns - scraper needs adjustment")
else:
    print("❌ Stonnington patterns not working - may need to check website manually")
