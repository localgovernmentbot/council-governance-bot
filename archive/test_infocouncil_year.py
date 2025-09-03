import requests
from bs4 import BeautifulSoup
import json
import re

def test_infocouncil_year_pattern():
    """Test the Year parameter pattern across all InfoCouncil councils"""
    
    # Load all councils
    with open('data/councils_full.json', 'r') as f:
        councils = json.load(f)['councils']
    
    # Get all InfoCouncil councils
    infocouncil_councils = [c for c in councils if c['platform'] == 'infocouncil' and c['council_id'] != 'MORE']  # Skip Moreland redirect
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print(f"Testing Year pattern on {len(infocouncil_councils)} InfoCouncil councils...")
    print("="*60)
    
    working_councils = []
    failed_councils = []
    
    # Test each council
    for i, council in enumerate(infocouncil_councils[:10]):  # Test first 10 for speed
        council_id = council['council_id']
        council_name = council['council_name']
        base_url = council['base_url']
        
        # Try different year patterns
        patterns_to_try = [
            f"/Default.aspx?Year=2025",
            f"/default.aspx?Year=2025",
            f"/Default.aspx?year=2025",
            f"/Open/2025/Council",
            f"/Open/2025/"
        ]
        
        found_working = False
        
        for pattern in patterns_to_try:
            if found_working:
                break
                
            url = base_url + pattern
            
            try:
                response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for meeting content
                    links = soup.find_all('a', href=True)
                    meeting_links = []
                    
                    for link in links:
                        href = link['href']
                        text = link.get_text(strip=True)
                        
                        # Look for meeting-related links
                        if any(term in href.lower() for term in ['meeting.aspx', 'download.aspx', '.pdf']) or \
                           any(term in text.lower() for term in ['agenda', 'minutes']):
                            meeting_links.append({
                                'text': text,
                                'href': href
                            })
                    
                    if meeting_links:
                        found_working = True
                        working_councils.append({
                            'council': council_name,
                            'council_id': council_id,
                            'pattern': pattern,
                            'link_count': len(meeting_links)
                        })
                        
                        print(f"\n✓ {council_name} ({council_id})")
                        print(f"  Working pattern: {pattern}")
                        print(f"  Meeting links: {len(meeting_links)}")
                        
                        # Show sample links
                        for ml in meeting_links[:3]:
                            if ml['text'].strip():  # Only show if has text
                                print(f"    - {ml['text'][:40]}...")
                        
            except Exception as e:
                pass
        
        if not found_working:
            failed_councils.append(council_name)
            print(f"\n✗ {council_name} ({council_id}) - No pattern worked")
    
    # Summary
    print(f"\n\n{'='*60}")
    print(f"SUMMARY: {len(working_councils)}/{len(infocouncil_councils[:10])} councils working")
    print(f"\nMost common pattern:")
    if working_councils:
        patterns = {}
        for wc in working_councils:
            patterns[wc['pattern']] = patterns.get(wc['pattern'], 0) + 1
        
        for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True):
            print(f"  '{pattern}' - worked for {count} councils")

if __name__ == "__main__":
    test_infocouncil_year_pattern()
