# scripts/find_meeting_docs.py
import requests
from bs4 import BeautifulSoup

def check_intranet_links():
    """Some councils use meeting management systems"""
    
    councils = [
        {
            'name': 'Port Phillip',
            'base_url': 'https://www.portphillip.vic.gov.au',
            'search_urls': [
                '/about-the-council/council-meetings/',
                '/about-the-council/council-meetings/meetings-and-agendas/',
                '/about-the-council/how-we-govern/council-documents/'
            ]
        },
        {
            'name': 'Stonnington',
            'base_url': 'https://www.stonnington.vic.gov.au',
            'search_urls': [
                '/About/Council-meetings',
                '/About/Council-and-committee-meetings',
                '/About/Council-meetings/Minutes-and-agendas'
            ]
        }
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    for council in councils:
        print(f"\n{'='*60}")
        print(f"Checking {council['name']}")
        
        for search_url in council['search_urls']:
            url = council['base_url'] + search_url
            print(f"\nTrying: {url}")
            
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for external meeting system links
                    external_links = soup.find_all('a', href=True)
                    for link in external_links:
                        href = link['href']
                        text = link.get_text(strip=True)
                        
                        # Common meeting management systems
                        if any(system in href.lower() for system in ['intranet', 'ecouncil', 'moderngov', 'civicclerk', 'legistar']):
                            print(f"  Found external system: {text}")
                            print(f"  URL: {href}")
                        
                        # Look for "View minutes" or "View agenda" type links
                        if any(action in text.lower() for action in ['view minutes', 'view agenda', 'download minutes', 'download agenda']):
                            print(f"  Found action link: {text}")
                            print(f"  URL: {href}")
                            
            except Exception as e:
                print(f"  Error: {e}")

check_intranet_links()