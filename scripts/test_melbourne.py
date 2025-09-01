import requests
from bs4 import BeautifulSoup
import json

def test_melbourne():
    """Test different Melbourne Council URLs"""
    
    # Try different URLs
    urls_to_try = [
        "https://www.melbourne.vic.gov.au/about-council/committees-meetings/meeting-archive/pages/meeting-archive.aspx",
        "https://www.melbourne.vic.gov.au/about-council/committees-meetings/Pages/CouncilMeetings.aspx",
        "https://www.melbourne.vic.gov.au/sitecollectiondocuments/meetings-calendar.htm",
        "https://www.melbourne.vic.gov.au/about-council/governance/pages/council-meetings.aspx"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for url in urls_to_try:
        print(f"\n{'='*50}")
        print(f"Testing: {url}")
        print('='*50)
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Basic page info
                title = soup.find('title')
                print(f"Page title: {title.text if title else 'No title'}")
                
                # Look for links
                all_links = soup.find_all('a', href=True)
                print(f"Total links: {len(all_links)}")
                
                # PDF links
                pdf_links = [a for a in all_links if '.pdf' in a.get('href', '').lower()]
                print(f"PDF links: {len(pdf_links)}")
                
                if pdf_links:
                    print("\nFirst 3 PDF links:")
                    for link in pdf_links[:3]:
                        print(f"- {link.get_text(strip=True)[:50]}...")
                        print(f"  {link['href'][:80]}...")
                
                # Look for content
                print(f"\nPage content preview: {response.text[:200]}...")
                
        except Exception as e:
            print(f"Error: {e}")

    # Try participate.melbourne.vic.gov.au which might have meeting info
    print(f"\n{'='*50}")
    print("Testing participate.melbourne.vic.gov.au API")
    print('='*50)
    
    try:
        # This is a common pattern for open data portals
        api_url = "https://data.melbourne.vic.gov.au/api/records/1.0/search/?dataset=council-meetings"
        response = requests.get(api_url, headers=headers, timeout=10)
        print(f"API Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"API Response: {json.dumps(data, indent=2)[:500]}...")
    except Exception as e:
        print(f"API Error: {e}")

if __name__ == "__main__":
    test_melbourne()