#!/usr/bin/env python3
"""
Test Yarra's actual meeting page structure
"""

import requests
from bs4 import BeautifulSoup

print("Testing Yarra Council Meeting Pages")
print("=" * 50)

# The URL you found
test_url = "https://www.yarracity.vic.gov.au/about-us/committees-meetings-and-minutes/council-meeting-12-august-2025"

print(f"Testing: {test_url}")
print()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

try:
    response = requests.get(test_url, headers=headers, timeout=30)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for download links
        print("\nLooking for download links...")
        download_links = soup.find_all("a", class_="download-link")
        print(f"Download links found: {len(download_links)}")
        
        for link in download_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            print(f"  - {text}: {href}")
        
        # Look for any PDF links
        print("\nLooking for PDF links...")
        pdf_links = soup.find_all('a', href=lambda x: x and '.pdf' in x.lower())
        print(f"PDF links found: {len(pdf_links)}")
        
        for link in pdf_links[:5]:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            print(f"  - {text}: {href}")
        
        # Look for headings
        print("\nPage headings:")
        for heading in soup.find_all(['h1', 'h2', 'h3'])[:5]:
            print(f"  - {heading.name}: {heading.get_text(strip=True)}")
        
        # Check if this matches YIMBY's pattern
        print("\nChecking YIMBY patterns...")
        
        # Date and time
        date_time_p = soup.find("strong", string="Date and time:")
        if date_time_p:
            print("  ✓ Found 'Date and time:' pattern")
            parent = date_time_p.find_parent("p")
            if parent:
                print(f"    Content: {parent.get_text(strip=True)}")
        
        # Address
        address_p = soup.find("strong", string="Address:")
        if address_p:
            print("  ✓ Found 'Address:' pattern")
            parent = address_p.find_parent("p")
            if parent:
                print(f"    Content: {parent.get_text(strip=True)}")
        
        # Now try to find the meetings list page
        print("\n\nTrying meetings list page...")
        list_url = "https://www.yarracity.vic.gov.au/about-us/committees-meetings-and-minutes"
        
        response2 = requests.get(list_url, headers=headers, timeout=30)
        if response2.status_code == 200:
            soup2 = BeautifulSoup(response2.text, 'html.parser')
            
            # Look for meeting links
            meeting_links = []
            for link in soup2.find_all('a', href=True):
                href = link.get('href', '')
                if 'council-meeting-' in href and '2025' in href:
                    meeting_links.append({
                        'text': link.get_text(strip=True),
                        'href': href
                    })
            
            print(f"\nFound {len(meeting_links)} meeting links for 2025:")
            for ml in meeting_links[:10]:
                print(f"  - {ml['text']}")
                print(f"    {ml['href']}")
        
    else:
        print(f"Failed with status code: {response.status_code}")
        
except Exception as e:
    print(f"Error: {e}")

print("\n\nCONCLUSION:")
print("Yarra has a different structure than expected!")
print("They use individual pages for each meeting.")
print("We need to:")
print("1. Find the list of meeting pages")
print("2. Visit each meeting page")
print("3. Extract the download links from each page")
