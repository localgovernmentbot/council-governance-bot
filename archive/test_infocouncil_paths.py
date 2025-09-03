import requests
from bs4 import BeautifulSoup

def test_infocouncil_paths():
    """Test common InfoCouncil paths across different councils"""
    
    # Common InfoCouncil paths based on typical patterns
    common_paths = [
        "/Open/2025/Council",
        "/Open/2024/Council", 
        "/Open/Meetings.aspx",
        "/Open/HomePage.aspx",
        "/Default.aspx",
        "/Open/SearchDocument.aspx?Year=2025",
        "/open.asp"
    ]
    
    # Test councils
    test_councils = [
        ("Banyule", "https://banyule.infocouncil.biz"),
        ("Darebin", "https://darebin.infocouncil.biz"),
        ("Whitehorse", "https://whitehorse.infocouncil.biz")
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for council_name, base_url in test_councils:
        print(f"\n{'='*60}")
        print(f"Testing {council_name}")
        print('='*60)
        
        for path in common_paths:
            url = base_url + path
            try:
                response = requests.get(url, headers=headers, timeout=5, allow_redirects=True)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Check if we found meeting content
                    text = soup.get_text()
                    has_meetings = any(word in text.lower() for word in ['agenda', 'minutes', 'meeting', '2025', '2024'])
                    
                    # Count links
                    links = soup.find_all('a', href=True)
                    meeting_links = [l for l in links if any(term in l['href'] for term in ['Meeting.aspx', 'Download.aspx', '.pdf'])]
                    
                    if has_meetings or meeting_links:
                        print(f"✓ {path} - Status: {response.status_code}")
                        print(f"  Final URL: {response.url}")
                        print(f"  Has meeting content: {has_meetings}")
                        print(f"  Meeting links: {len(meeting_links)}")
                        
                        # Show first few meeting links
                        for link in meeting_links[:3]:
                            print(f"    - {link.get_text(strip=True)[:40]}...")
                
            except Exception as e:
                pass  # Skip errors for brevity

if __name__ == "__main__":
    test_infocouncil_paths()
