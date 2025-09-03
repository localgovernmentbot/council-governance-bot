#!/usr/bin/env python3
"""
Debug Port Phillip InfoCouncil
"""

import requests
from bs4 import BeautifulSoup
import re

print("Debugging Port Phillip InfoCouncil")
print("=" * 50)

base_url = "https://portphillip.infocouncil.biz"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# Test 1: Check if site is accessible
print("\n1. Testing base URL...")
try:
    response = requests.get(base_url, headers=headers, timeout=30)
    print(f"Status: {response.status_code}")
    print(f"URL after redirect: {response.url}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Try the direct URLs you provided
print("\n2. Testing your provided URLs...")
test_urls = [
    "https://portphillip.infocouncil.biz/Open/2025/09/ORD_02092025_AGN_AT_WEB.htm",
    "https://portphillip.infocouncil.biz/RedirectToDoc.aspx?URL=Open/2025/09/ORD_02092025_AGN_AT.PDF"
]

for url in test_urls:
    try:
        response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        print(f"\nURL: {url}")
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
        print(f"Size: {len(response.content)} bytes")
    except Exception as e:
        print(f"Error: {e}")

# Test 3: Try the Open directory
print("\n3. Testing Open directory...")
open_url = f"{base_url}/Open/"
try:
    response = requests.get(open_url, headers=headers, timeout=30)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for any links
        links = soup.find_all('a', href=True)
        print(f"Links found: {len(links)}")
        
        # Show first few links
        for link in links[:10]:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            if text and 'parent' not in text.lower():
                print(f"  - {text}: {href}")
                
except Exception as e:
    print(f"Error: {e}")

# Test 4: Try specific month
print("\n4. Testing specific month (September 2025)...")
month_url = f"{base_url}/Open/2025/09/"
try:
    response = requests.get(month_url, headers=headers, timeout=30)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for meeting files
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if 'ORD_' in href or '.PDF' in href.upper():
                print(f"  Found: {link.get_text(strip=True)} -> {href}")
                
except Exception as e:
    print(f"Error: {e}")

print("\n\nConclusion:")
print("Port Phillip InfoCouncil might:")
print("1. Require authentication")
print("2. Block automated requests")
print("3. Use JavaScript to load content")
print("4. Have a different structure than expected")
