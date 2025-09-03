"""
Debug Melbourne scraper to see why it's not finding documents
"""

import requests
from bs4 import BeautifulSoup

url = "https://www.melbourne.vic.gov.au/about-council/committees-meetings/meeting-archive/pages/meeting-archive.aspx"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print("Checking Melbourne meeting archive page...")
print(f"URL: {url}")

try:
    response = requests.get(url, headers=headers, timeout=30)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check for any PDFs
        all_links = soup.find_all('a', href=True)
        pdf_links = [a for a in all_links if '.pdf' in a['href'].lower()]
        s3_links = [a for a in all_links if 's3' in a['href'].lower()]
        
        print(f"\nTotal links: {len(all_links)}")
        print(f"PDF links: {len(pdf_links)}")
        print(f"S3 links: {len(s3_links)}")
        
        # Show sample links
        if pdf_links:
            print("\nSample PDF links:")
            for link in pdf_links[:3]:
                print(f"  Text: {link.get_text(strip=True)}")
                print(f"  URL: {link['href'][:80]}...")
        
        # Look for any meeting-related text
        meeting_links = [a for a in all_links if any(word in a.get_text(strip=True).lower() for word in ['agenda', 'minutes', '2025', '2024'])]
        print(f"\nMeeting-related links: {len(meeting_links)}")
        
        if meeting_links and not pdf_links:
            print("\nMeeting links found (no PDFs):")
            for link in meeting_links[:5]:
                print(f"  - {link.get_text(strip=True)}")
                
except Exception as e:
    print(f"Error: {e}")
