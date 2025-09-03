"""
Debug Hobsons Bay meeting pages to understand structure
"""

import requests
from bs4 import BeautifulSoup

# Test URL from a specific meeting
base_url = "https://www.hobsonsbay.vic.gov.au"
test_meeting_url = "https://www.hobsonsbay.vic.gov.au/Council/Council-meetings/Minutes-and-agendas"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print("Debugging Hobsons Bay structure...")
print("=" * 60)

# First check the main page
response = requests.get(test_meeting_url, headers=headers)
print(f"Main page status: {response.status_code}")

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all links
    all_links = soup.find_all('a', href=True)
    
    # Look for meeting links
    meeting_links = []
    for link in all_links:
        text = link.get_text(strip=True)
        if any(year in text for year in ['2025', '2024']) and 'meeting' in text.lower():
            meeting_links.append({
                'text': text,
                'href': link['href']
            })
    
    print(f"\nFound {len(meeting_links)} meeting links")
    
    if meeting_links:
        # Check the first meeting
        first_meeting = meeting_links[0]
        print(f"\nChecking first meeting: {first_meeting['text']}")
        
        # Make URL absolute
        meeting_url = first_meeting['href']
        if not meeting_url.startswith('http'):
            meeting_url = base_url + meeting_url if meeting_url.startswith('/') else base_url + '/' + meeting_url
        
        print(f"Meeting URL: {meeting_url}")
        
        # Fetch meeting page
        meeting_response = requests.get(meeting_url, headers=headers, timeout=10)
        print(f"Meeting page status: {meeting_response.status_code}")
        
        if meeting_response.status_code == 200:
            meeting_soup = BeautifulSoup(meeting_response.text, 'html.parser')
            
            # Look for PDFs
            pdf_links = meeting_soup.find_all('a', href=lambda x: x and '.pdf' in x.lower())
            print(f"\nPDF links found: {len(pdf_links)}")
            
            for pdf in pdf_links[:5]:
                print(f"\nPDF Text: {pdf.get_text(strip=True)}")
                print(f"PDF Href: {pdf['href']}")
            
            # If no PDFs, look for download links
            if not pdf_links:
                download_links = meeting_soup.find_all('a', href=lambda x: x and 'download' in x.lower())
                print(f"\nDownload links: {len(download_links)}")
                
                # Also check for any links with agenda/minutes text
                agenda_links = [a for a in meeting_soup.find_all('a') if 'agenda' in a.get_text(strip=True).lower()]
                minutes_links = [a for a in meeting_soup.find_all('a') if 'minutes' in a.get_text(strip=True).lower()]
                
                print(f"Agenda-related links: {len(agenda_links)}")
                print(f"Minutes-related links: {len(minutes_links)}")
