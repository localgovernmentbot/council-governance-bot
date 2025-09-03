import requests
from bs4 import BeautifulSoup

# Test Alpine Shire council meetings
url = "https://www.alpineshire.vic.gov.au/about-us/our-council/council-meetings"
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})

print(f"Testing Alpine Shire: {url}")
print(f"Status: {response.status_code}")

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all links
    all_links = soup.find_all('a', href=True)
    print(f"\nTotal links: {len(all_links)}")
    
    # PDF links
    pdf_links = [a for a in all_links if '.pdf' in a['href'].lower()]
    print(f"PDF links: {len(pdf_links)}")
    
    if pdf_links:
        print("\nPDF documents found:")
        for link in pdf_links[:5]:
            print(f"- {link.get_text(strip=True)}")
            print(f"  URL: {link['href']}")
    
    # Meeting links
    meeting_links = [a for a in all_links if any(word in a.get_text(strip=True).lower() for word in ['agenda', 'minutes', '2025', '2024'])]
    print(f"\nMeeting-related links: {len(meeting_links)}")
    
    if meeting_links and not pdf_links:
        print("\nMeeting links (no direct PDFs):")
        for link in meeting_links[:5]:
            print(f"- {link.get_text(strip=True)}")
