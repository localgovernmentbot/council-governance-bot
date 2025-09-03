"""
Test scraper for Alpine Shire to find the correct URL structure
"""

import requests
from bs4 import BeautifulSoup

def explore_alpine_shire():
    """Find where Alpine Shire keeps their meeting PDFs"""
    
    print("Exploring Alpine Shire council meeting structure...")
    print("=" * 60)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # Try different URL patterns based on what we found
    urls_to_try = [
        "https://www.alpineshire.vic.gov.au/council-meetings",
        "https://www.alpineshire.vic.gov.au/about-us/our-council/council-meetings",
        "https://www.alpineshire.vic.gov.au/about-us/our-council/meetings",
        "https://www.alpineshire.vic.gov.au/about-us/our-council/agendas-minutes"
    ]
    
    for url in urls_to_try:
        print(f"\nTrying: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for PDF links
                pdf_links = soup.find_all('a', href=lambda x: x and '.pdf' in x.lower())
                print(f"PDF links found: {len(pdf_links)}")
                
                if pdf_links:
                    print("Sample PDFs:")
                    for link in pdf_links[:3]:
                        print(f"  - {link.get_text(strip=True)}")
                        print(f"    URL: {link['href']}")
                
                # Look for links to meeting pages
                meeting_links = []
                for link in soup.find_all('a', href=True):
                    text = link.get_text(strip=True).lower()
                    if any(word in text for word in ['agenda', 'minutes', '2025', '2024']):
                        meeting_links.append(link)
                
                if meeting_links and not pdf_links:
                    print(f"Found {len(meeting_links)} meeting-related links (no direct PDFs)")
                    for link in meeting_links[:3]:
                        print(f"  - {link.get_text(strip=True)}")
                
        except Exception as e:
            print(f"Error: {e}")
    
    # Also check if they use a different system
    print("\n\nChecking for external meeting systems...")
    external_patterns = [
        "intranet.alpine",
        "ecouncil",
        "moderngov",
        "infocouncil"
    ]
    
    try:
        response = requests.get(urls_to_try[1], headers=headers, timeout=10)
        if response.status_code == 200:
            for pattern in external_patterns:
                if pattern in response.text.lower():
                    print(f"Found reference to: {pattern}")
    except:
        pass

if __name__ == "__main__":
    explore_alpine_shire()
