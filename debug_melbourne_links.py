"""
Debug Melbourne - examine actual document links
"""

import requests
from bs4 import BeautifulSoup

url = "https://www.melbourne.vic.gov.au/about-council/committees-meetings/meeting-archive/pages/meeting-archive.aspx"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers, timeout=30)
soup = BeautifulSoup(response.text, 'html.parser')

print("Melbourne document links analysis:")
print("=" * 60)

# Find all PDF and S3 links
document_links = []
for link in soup.find_all('a', href=True):
    href = link.get('href', '')
    text = link.get_text(strip=True)
    
    if '.pdf' in href.lower() or ('s3' in href.lower() and 'amazonaws' in href.lower()):
        document_links.append({
            'text': text,
            'href': href
        })

print(f"\nFound {len(document_links)} document links")

# Show all document links to understand the pattern
for i, doc in enumerate(document_links[:10]):
    print(f"\n{i+1}. Text: '{doc['text']}'")
    print(f"   Href: {doc['href']}")
    
    # Check if it has date/meeting keywords
    has_date = any(month in doc['text'] for month in ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'])
    has_meeting_word = any(word in doc['text'].lower() for word in ['agenda', 'minutes', 'meeting'])
    
    print(f"   Has date: {has_date}, Has meeting word: {has_meeting_word}")
