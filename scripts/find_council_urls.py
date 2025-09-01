import requests
from bs4 import BeautifulSoup

def find_meeting_pages():
    """Try to find the correct meeting pages for councils"""
    
    councils_to_check = [
        {
            'name': 'City of Yarra',
            'base': 'https://www.yarracity.vic.gov.au',
            'search_terms': ['council meetings', 'agendas', 'minutes']
        },
        {
            'name': 'City of Port Phillip',
            'base': 'https://www.portphillip.vic.gov.au',
            'search_terms': ['council meetings', 'agendas']
        },
        {
            'name': 'Darebin City Council',
            'base': 'https://www.darebin.vic.gov.au',
            'search_terms': ['council meetings', 'agendas']
        },
        {
            'name': 'City of Maribyrnong',
            'base': 'https://www.maribyrnong.vic.gov.au',
            'search_terms': ['council meetings']
        },
        {
            'name': 'Merri-bek City Council',
            'base': 'https://www.merri-bek.vic.gov.au',
            'search_terms': ['council meetings']
        }
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for council in councils_to_check:
        print(f"\nChecking {council['name']}...")
        print(f"Base URL: {council['base']}")
        
        try:
            # Try the homepage
            response = requests.get(council['base'], headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for links containing meeting-related terms
                links = soup.find_all('a', href=True)
                meeting_links = []
                
                for link in links:
                    text = link.get_text(strip=True).lower()
                    href = link['href']
                    
                    if any(term in text for term in council['search_terms']):
                        if not href.startswith('http'):
                            href = council['base'] + href
                        meeting_links.append((text, href))
                
                if meeting_links:
                    print("Found potential meeting pages:")
                    for text, url in meeting_links[:5]:  # Show first 5
                        print(f"  - {text}: {url}")
                else:
                    print("  No meeting links found on homepage")
                    
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    find_meeting_pages()