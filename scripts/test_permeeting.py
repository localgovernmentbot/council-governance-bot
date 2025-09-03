import requests
from bs4 import BeautifulSoup

def test_permeeting_councils():
    """Test if other per-meeting councils work like Melbourne"""
    
    permeeting_councils = [
        {
            'council_id': 'HBAY',
            'name': 'Hobsons Bay City',
            'url': 'https://www.hobsonsbay.vic.gov.au/Council/Council-meetings/Minutes-and-agendas'
        },
        {
            'council_id': 'MARI',
            'name': 'Maribyrnong City',
            'url': 'https://www.maribyrnong.vic.gov.au/council-meetings'
        },
        {
            'council_id': 'MELT',
            'name': 'Melton City',
            'url': 'https://www.melton.vic.gov.au/council/minutes-agendas'
        }
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print("Testing per-meeting councils...")
    print("="*60)
    
    for council in permeeting_councils:
        print(f"\n{council['name']} ({council['council_id']})")
        print(f"URL: {council['url']}")
        print("-"*40)
        
        try:
            response = requests.get(council['url'], headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for patterns similar to Melbourne
                # Melbourne has S3 links, but others might have different patterns
                pdf_links = []
                meeting_page_links = []
                
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    text = link.get_text(strip=True)
                    
                    # Direct PDF links
                    if '.pdf' in href.lower():
                        pdf_links.append({'text': text, 'href': href})
                    
                    # Links to meeting pages (might need to follow these)
                    elif any(word in text.lower() for word in ['agenda', 'minutes', '2025', '2024', 'august', 'july']):
                        meeting_page_links.append({'text': text, 'href': href})
                
                print(f"Direct PDF links: {len(pdf_links)}")
                for pdf in pdf_links[:3]:
                    print(f"  - {pdf['text'][:50]}...")
                
                print(f"\nPotential meeting page links: {len(meeting_page_links)}")
                for link in meeting_page_links[:5]:
                    print(f"  - {link['text'][:50]}...")
                    
            else:
                print(f"Error: Status {response.status_code}")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_permeeting_councils()
