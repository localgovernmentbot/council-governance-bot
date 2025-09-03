"""
Test multiple CoreCMS councils to find the easiest ones to scrape
"""

import requests
from bs4 import BeautifulSoup
import json

def test_council(council):
    """Test a single council for PDF availability"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(council['url'], headers=headers, timeout=5)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Count PDFs
            pdf_count = 0
            for link in soup.find_all('a', href=True):
                if '.pdf' in link['href'].lower():
                    pdf_count += 1
            
            return {
                'council': council['name'],
                'status': response.status_code,
                'pdf_count': pdf_count,
                'url': council['url']
            }
        else:
            return {
                'council': council['name'],
                'status': response.status_code,
                'pdf_count': 0,
                'url': council['url']
            }
            
    except Exception as e:
        return {
            'council': council['name'],
            'status': 'error',
            'pdf_count': 0,
            'url': council['url'],
            'error': str(e)
        }

def main():
    # Load councils
    with open('data/councils_full.json', 'r') as f:
        all_councils = json.load(f)['councils']
    
    # Get CoreCMS councils we don't have scrapers for
    missing_corecms = []
    yimby_councils = ['melbourne', 'darebin', 'yarra', 'banyule', 'bayside', 'boroondara', 
                      'glen_eira', 'hobsons_bay', 'kingston', 'manningham', 'maribyrnong',
                      'merribek', 'monash', 'moonee_valley', 'port_phillip', 'stonnington', 
                      'whitehorse']
    
    for council in all_councils:
        if council['platform'] == 'corecms':
            council_name_simple = council['council_name'].lower().replace(' city', '').replace(' shire', '').replace(' ', '_')
            if council_name_simple not in yimby_councils:
                missing_corecms.append({
                    'id': council['council_id'],
                    'name': council['council_name'],
                    'url': council['base_url']
                })
    
    print("Testing CoreCMS councils for easy PDF access...")
    print("=" * 60)
    print(f"Testing first 10 of {len(missing_corecms)} missing CoreCMS councils\n")
    
    # Test first 10
    results = []
    for council in missing_corecms[:10]:
        print(f"Testing {council['name']}...", end='', flush=True)
        result = test_council(council)
        results.append(result)
        print(f" Status: {result['status']}, PDFs: {result['pdf_count']}")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY - Councils with direct PDF access:")
    print("=" * 60)
    
    working_councils = [r for r in results if r['pdf_count'] > 0]
    working_councils.sort(key=lambda x: x['pdf_count'], reverse=True)
    
    if working_councils:
        for council in working_councils:
            print(f"\n{council['council']} - {council['pdf_count']} PDFs")
            print(f"  URL: {council['url']}")
    else:
        print("\nNo councils found with direct PDF access in this batch.")
        print("These councils likely need more complex scraping approaches.")

if __name__ == "__main__":
    main()
