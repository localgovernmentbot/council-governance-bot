"""
Debug Hobsons Bay - find actual meeting pages
"""

import requests
from bs4 import BeautifulSoup
import re

base_url = "https://www.hobsonsbay.vic.gov.au"
main_url = "https://www.hobsonsbay.vic.gov.au/Council/Council-meetings/Minutes-and-agendas"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print("Finding Hobsons Bay meeting structure...")
print("=" * 60)

response = requests.get(main_url, headers=headers)
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Look for links with dates
    all_links = soup.find_all('a', href=True)
    
    # Find links with date patterns
    date_pattern = r'\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}'
    
    meeting_links = []
    for link in all_links:
        text = link.get_text(strip=True)
        if re.search(date_pattern, text) and 'meeting' in text.lower():
            # Skip timetable links
            if 'timetable' not in text.lower():
                meeting_links.append({
                    'text': text,
                    'href': link['href']
                })
    
    print(f"Found {len(meeting_links)} dated meeting links")
    
    # Show first few
    for i, meeting in enumerate(meeting_links[:3]):
        print(f"\n{i+1}. {meeting['text']}")
        print(f"   Href: {meeting['href']}")
        
        # Check if it's a direct PDF
        if '.pdf' in meeting['href'].lower():
            print("   -> Direct PDF link!")
        else:
            # Try to fetch this page
            meeting_url = meeting['href']
            if not meeting_url.startswith('http'):
                meeting_url = base_url + meeting_url if meeting_url.startswith('/') else base_url + '/' + meeting_url
            
            try:
                meeting_resp = requests.get(meeting_url, headers=headers, timeout=10)
                if meeting_resp.status_code == 200:
                    meeting_soup = BeautifulSoup(meeting_resp.text, 'html.parser')
                    
                    # Look for PDFs or documents
                    pdfs = meeting_soup.find_all('a', href=lambda x: x and '.pdf' in x.lower())
                    docs = meeting_soup.find_all('a', href=lambda x: x and any(word in x.lower() for word in ['.pdf', '.doc', 'download']))
                    
                    print(f"   -> Meeting page has {len(pdfs)} PDFs, {len(docs)} total documents")
                    
                    # Show what we find
                    for pdf in pdfs[:2]:
                        print(f"      PDF: {pdf.get_text(strip=True)}")
            except:
                print("   -> Error fetching meeting page")
