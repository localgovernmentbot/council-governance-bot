import requests
from bs4 import BeautifulSoup
import json

def test_council(council):
    """Test a single council website"""
    print(f"\n{'='*60}")
    print(f"Testing: {council['name']}")
    print(f"URL: {council['meetings_url']}")
    print('='*60)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(council['meetings_url'], headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for PDF links
            all_links = soup.find_all('a', href=True)
            pdf_links = [a for a in all_links if '.pdf' in a.get('href', '').lower()]
            
            print(f"Total links: {len(all_links)}")
            print(f"PDF links: {len(pdf_links)}")
            
            # Show first 3 PDFs
            if pdf_links:
                print("\nFirst few PDFs found:")
                for link in pdf_links[:3]:
                    text = link.get_text(strip=True)
                    href = link['href']
                    if not href.startswith('http'):
                        href = council['url'] + href
                    print(f"- {text[:60]}...")
                    print(f"  {href[:80]}...")
            
            # Look for keywords
            text_content = soup.get_text().lower()
            has_agenda = 'agenda' in text_content
            has_minutes = 'minutes' in text_content
            print(f"\nContains 'agenda': {has_agenda}")
            print(f"Contains 'minutes': {has_minutes}")
            
    except Exception as e:
        print(f"Error: {e}")

def main():
    # Load councils
    with open('data/councils.json', 'r') as f:
        councils = json.load(f)['councils']
    
    print("Testing M9 Council Websites")
    print("="*60)
    
    for council in councils:
        test_council(council)
        
    print("\n\nSummary: Tested {} councils".format(len(councils)))

if __name__ == "__main__":
    main()