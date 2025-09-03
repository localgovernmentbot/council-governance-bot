"""
Test Greater Geelong (CoreCMS) to see if it's easier than Alpine
"""

import requests
from bs4 import BeautifulSoup
import json

def test_geelong():
    """Test Greater Geelong council meetings page"""
    
    print("Testing Greater Geelong City Council")
    print("=" * 60)
    
    # From our data, Geelong's URL
    url = "https://www.geelongaustralia.com.au/meetings/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"URL: {url}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for PDF links
            pdf_links = []
            for link in soup.find_all('a', href=True):
                if '.pdf' in link['href'].lower():
                    pdf_links.append({
                        'text': link.get_text(strip=True),
                        'href': link['href']
                    })
            
            print(f"\nPDF links found: {len(pdf_links)}")
            
            if pdf_links:
                print("\nSample PDFs:")
                for pdf in pdf_links[:5]:
                    print(f"  - {pdf['text']}")
                    print(f"    URL: {pdf['href']}")
                    
                return True
            else:
                # Look for other patterns
                print("\nNo direct PDFs. Looking for meeting links...")
                
                # Check for links with meeting keywords
                meeting_links = []
                for link in soup.find_all('a', href=True):
                    text = link.get_text(strip=True)
                    if any(word in text.lower() for word in ['agenda', 'minutes', 'meeting', '2025', '2024']):
                        meeting_links.append({
                            'text': text,
                            'href': link['href']
                        })
                
                print(f"Meeting-related links: {len(meeting_links)}")
                for ml in meeting_links[:5]:
                    print(f"  - {ml['text']}")
                
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_geelong()
