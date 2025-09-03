"""
Debug remaining M9 councils
"""

import requests
from bs4 import BeautifulSoup

print("Debugging remaining M9 councils...")
print("=" * 60)

# Test different approaches for each council

print("\n1. MOONEE VALLEY")
print("-" * 30)
urls = [
    "https://mvcc.vic.gov.au/my-council/council-meetings/",
    "https://mvcc.vic.gov.au/my-council/meetings-agendas-and-minutes/"
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

for url in urls:
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"URL: {url}")
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Look for tables
            tables = soup.find_all('table')
            print(f"Tables found: {len(tables)}")
            
            # Look for PDFs
            pdfs = soup.find_all('a', href=lambda x: x and '.pdf' in x.lower())
            print(f"PDF links: {len(pdfs)}")
            
            # Look for any meeting links
            meeting_links = [a for a in soup.find_all('a') if any(w in a.get_text(strip=True).lower() for w in ['agenda', 'minutes', '2025', '2024'])]
            print(f"Meeting links: {len(meeting_links)}")
            
            if pdfs:
                print("Sample PDFs:")
                for pdf in pdfs[:3]:
                    print(f"  - {pdf.get_text(strip=True)}")
                    
    except Exception as e:
        print(f"Error: {e}")

print("\n\n2. YARRA")
print("-" * 30)
# Yarra blocks requests, might need different approach
print("Yarra returns 403 Forbidden - may require browser headers or Selenium")

print("\n\n3. PORT PHILLIP")
print("-" * 30)
url = "https://www.portphillip.vic.gov.au/about-the-council/meetings-and-minutes"
try:
    # Try with shorter timeout
    resp = requests.get(url, headers=headers, timeout=5)
    print(f"Status: {resp.status_code}")
except:
    print("Timeout - trying alternate URL")
    # Try base URL
    try:
        resp = requests.get("https://www.portphillip.vic.gov.au", headers=headers, timeout=5)
        print(f"Base URL status: {resp.status_code}")
    except:
        print("Port Phillip site appears to be slow/blocking")

print("\n\n4. STONNINGTON")
print("-" * 30)
urls = [
    "https://stonnington.infocouncil.biz",
    "https://stonnington.infocouncil.biz/Open/",
    "https://www.stonnington.vic.gov.au/About/Council/Council-meetings"
]

for url in urls:
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"URL: {url}")
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Look for meeting links
            links = soup.find_all('a', href=True)
            meeting_links = [a for a in links if any(w in a.get_text(strip=True).lower() for w in ['agenda', 'minutes', 'meeting'])]
            print(f"Meeting links: {len(meeting_links)}")
            
            if meeting_links:
                print("Sample links:")
                for link in meeting_links[:3]:
                    print(f"  - {link.get_text(strip=True)}")
                    
    except Exception as e:
        print(f"Error: {e}")
