# scripts/debug_council.py
import requests
from bs4 import BeautifulSoup

def debug_port_phillip():
    url = "https://www.portphillip.vic.gov.au/about-the-council/council-meetings/meetings-and-agendas/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all PDFs
    all_links = soup.find_all('a', href=True)
    pdf_links = [a for a in all_links if '.pdf' in a.get('href', '').lower()]
    
    print(f"Found {len(pdf_links)} PDF links:")
    for link in pdf_links[:10]:  # Show first 10
        text = link.get_text(strip=True)
        href = link['href']
        print(f"\nText: {text}")
        print(f"URL: {href}")
        print(f"Contains 'agenda': {'agenda' in text.lower()}")
        print(f"Contains 'minutes': {'minutes' in text.lower()}")

if __name__ == "__main__":
    debug_port_phillip()