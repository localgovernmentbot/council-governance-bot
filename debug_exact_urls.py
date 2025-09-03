#!/usr/bin/env python3
"""
Debug Yarra and Stonnington with exact URLs
"""

import requests

print("Debugging Yarra and Stonnington with exact URLs")
print("=" * 50)

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# Test Yarra - exact URLs from the pattern
print("\n1. YARRA - Testing exact URLs:")
yarra_tests = [
    # PDC patterns
    "https://www.yarracity.vic.gov.au/sites/default/files/2025-08/20250826-pdc-agenda.pdf",
    "https://www.yarracity.vic.gov.au/sites/default/files/2025-08/20250826_pdc_agenda.pdf",
    "https://www.yarracity.vic.gov.au/sites/default/files/2025-07/20250722-pdc-agenda.pdf",
    "https://www.yarracity.vic.gov.au/sites/default/files/2025-07/20250722_pdc_agenda.pdf",
    # Council minutes patterns
    "https://www.yarracity.vic.gov.au/sites/default/files/2025-08/20250812-council-minutes.pdf",
    "https://www.yarracity.vic.gov.au/sites/default/files/2025-08/minutes_ordinary_council_meeting_12_august_2025.pdf",
    # The one you found
    "https://www.yarracity.vic.gov.au/sites/default/files/2025-08/ordinary_council_meeting_minutes_-_tuesday_12_august_2025.pdf",
    "https://www.yarracity.vic.gov.au/sites/default/files/2025-08/ordinary_council_meeting_agenda_-_tuesday_12_august_2025.pdf"
]

for url in yarra_tests:
    try:
        resp = requests.head(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            print(f"✓ FOUND: {url}")
        else:
            print(f"✗ {resp.status_code}: {url}")
    except Exception as e:
        print(f"✗ Error: {url} - {e}")

# Test Stonnington - exact URLs from the pattern
print("\n\n2. STONNINGTON - Testing exact URLs:")
stonnington_tests = [
    # August 25 patterns
    "https://www.stonnington.vic.gov.au/files/assets/public/v/2/about/council-meetings/2025/25-august-2025/agenda.pdf",
    "https://www.stonnington.vic.gov.au/files/assets/public/v/2/about/council-meetings/2025/25-august-2025/agenda-council-meeting-25-august-2025.pdf",
    # August 11 patterns
    "https://www.stonnington.vic.gov.au/files/assets/public/v/2/about/council-meetings/2025/11-august-2025/agenda.pdf",
    # July 28 patterns
    "https://www.stonnington.vic.gov.au/files/assets/public/v/2/about/council-meetings/2025/28-july-2025/agenda.pdf",
    # Check v/1 instead of v/2
    "https://www.stonnington.vic.gov.au/files/assets/public/v/1/about/council-meetings/2025/25-august-2025/agenda.pdf",
    # The ZIP you found
    "https://www.stonnington.vic.gov.au/ocapi/Public/files/zipall/1225e61e-4a97-44a7-8de7-012a92869e3b/file/25%20Aug%202025_-_Ordinary_Meeting.zip",
    # The PDF you found
    "https://www.stonnington.vic.gov.au/files/assets/public/v/1/about/council-meetings/2025/25-aug-2025/agenda-council-meeting-25-august-2025.pdf"
]

for url in stonnington_tests:
    try:
        resp = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
        if resp.status_code == 200:
            print(f"✓ FOUND: {url}")
        else:
            print(f"✗ {resp.status_code}: {url}")
    except Exception as e:
        print(f"✗ Error: {url} - {e}")

print("\n\nKey findings:")
print("- Check which exact URLs work")
print("- Note the exact folder structure (v/1 vs v/2)")
print("- Note the exact date format in folders")
