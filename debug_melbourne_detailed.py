"""
Debug Melbourne scraper - check current page structure
"""

import requests
from bs4 import BeautifulSoup

urls_to_test = [
    "https://www.melbourne.vic.gov.au/about-council/committees-meetings/meeting-archive/pages/meeting-archive.aspx",
    "https://www.melbourne.vic.gov.au/about-council/committees-meetings/Pages/default.aspx",
    "https://www.melbourne.vic.gov.au/about-council/committees-meetings/Pages/CouncilMeetings.aspx"
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print("Debugging Melbourne Council website structure...")
print("=" * 60)

for url in urls_to_test:
    print(f"\nTesting: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Count different types of links
            all_links = soup.find_all('a', href=True)
            pdf_links = [a for a in all_links if '.pdf' in a['href'].lower()]
            s3_links = [a for a in all_links if 's3' in a['href'].lower()]
            aspx_links = [a for a in all_links if '.aspx' in a['href'].lower()]
            
            print(f"  Total links: {len(all_links)}")
            print(f"  PDF links: {len(pdf_links)}")
            print(f"  S3 links: {len(s3_links)}")
            print(f"  ASPX links: {len(aspx_links)}")
            
            # Look for meeting-related links
            meeting_keywords = ['meeting', 'agenda', 'minutes', '2025', '2024', 'august', 'july']
            meeting_links = []
            
            for link in all_links:
                text = link.get_text(strip=True).lower()
                if any(keyword in text for keyword in meeting_keywords):
                    meeting_links.append({
                        'text': link.get_text(strip=True),
                        'href': link['href']
                    })
            
            print(f"  Meeting-related links: {len(meeting_links)}")
            
            # Show sample meeting links
            if meeting_links:
                print("\n  Sample meeting links:")
                for ml in meeting_links[:5]:
                    print(f"    - {ml['text']}")
                    print(f"      {ml['href'][:80]}...")
            
            # Check page title and content
            title = soup.find('title')
            if title:
                print(f"\n  Page title: {title.text.strip()}")
                
    except Exception as e:
        print(f"Error: {e}")

# Also check if they have a different structure
print("\n\nChecking for alternative meeting pages...")
alt_url = "https://www.melbourne.vic.gov.au/SiteCollectionPages/council-meetings.aspx"
try:
    response = requests.get(alt_url, headers=headers, timeout=10)
    if response.status_code == 200:
        print(f"Alternative page found: {alt_url}")
except:
    pass
