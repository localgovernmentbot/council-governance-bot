# scripts/debug_council_detailed.py
import requests
from bs4 import BeautifulSoup

def debug_council_detailed(council_name, url):
    print(f"\n{'='*60}")
    print(f"Debugging {council_name}")
    print(f"URL: {url}")
    print('='*60)
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Look for common section headers
    print("\nLooking for meeting-related sections...")
    for header in soup.find_all(['h1', 'h2', 'h3', 'h4']):
        text = header.get_text(strip=True)
        if any(word in text.lower() for word in ['meeting', 'agenda', 'minutes', '2025', '2024']):
            print(f"Found header: {text}")
    
    # Look for date patterns in any text
    print("\nLooking for date patterns in links...")
    all_links = soup.find_all('a', href=True)
    meeting_links = []
    
    for link in all_links:
        text = link.get_text(strip=True)
        parent_text = link.parent.get_text(strip=True) if link.parent else ""
        
        # Check if dates are mentioned nearby
        if any(month in text + parent_text for month in ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August']):
            if link['href'].endswith('.pdf') or 'PDF' in text:
                meeting_links.append((text, link['href'], parent_text[:100]))
    
    print(f"\nFound {len(meeting_links)} links with date references:")
    for text, href, context in meeting_links[:5]:
        print(f"\nLink text: {text}")
        print(f"Context: {context}...")
        print(f"URL: {href}")

# Test Port Phillip and Stonnington
debug_council_detailed("Port Phillip", "https://www.portphillip.vic.gov.au/about-the-council/council-meetings/meetings-and-agendas/")
debug_council_detailed("Stonnington", "https://www.stonnington.vic.gov.au/About/Council-meetings")