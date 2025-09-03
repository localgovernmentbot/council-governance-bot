# scripts/find_correct_urls.py
import requests
from bs4 import BeautifulSoup

def find_council_meeting_urls():
    """Try to find correct meeting URLs for councils with 404s"""
    
    councils_to_fix = [
        ("Banyule", "https://www.banyule.vic.gov.au"),
        ("Boroondara", "https://www.boroondara.vic.gov.au"),
        ("Brimbank", "https://www.brimbank.vic.gov.au"),
        ("Cardinia", "https://www.cardinia.vic.gov.au"),
        ("Casey", "https://www.casey.vic.gov.au"),
        ("Frankston", "https://www.frankston.vic.gov.au"),
        ("Glen Eira", "https://www.gleneira.vic.gov.au"),
        ("Hume", "https://www.hume.vic.gov.au"),
        ("Kingston", "https://www.kingston.vic.gov.au"),
        ("Knox", "https://www.knox.vic.gov.au"),
        ("Maroondah", "https://www.maroondah.vic.gov.au"),
        ("Melton", "https://www.melton.vic.gov.au"),
        ("Mornington Peninsula", "https://www.mornpen.vic.gov.au"),
        ("Whittlesea", "https://www.whittlesea.vic.gov.au"),
        ("Wyndham", "https://www.wyndham.vic.gov.au")
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    for name, base_url in councils_to_fix:
        print(f"\nSearching {name}...")
        
        try:
            # Try homepage
            response = requests.get(base_url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for meeting-related links
                links = soup.find_all('a', href=True)
                meeting_links = []
                
                for link in links:
                    text = link.get_text(strip=True).lower()
                    href = link['href'].lower()
                    
                    if any(term in text or term in href for term in ['council meeting', 'meeting', 'agenda', 'minutes']):
                        full_url = link['href']
                        if not full_url.startswith('http'):
                            full_url = base_url + link['href']
                        
                        # Skip generic links
                        if not any(skip in full_url for skip in ['contact', 'about-us/councillors', 'elected']):
                            meeting_links.append((link.get_text(strip=True), full_url))
                
                # Show unique links
                seen = set()
                for text, url in meeting_links[:5]:
                    if url not in seen:
                        print(f"  Found: {text}")
                        print(f"  URL: {url}")
                        seen.add(url)
                        
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    find_council_meeting_urls()