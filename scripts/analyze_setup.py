import json

def analyze_current_setup():
    """Analyze our current setup and identify quick wins"""
    
    # Load the original councils we were testing
    with open('data/councils.json', 'r') as f:
        original_councils = json.load(f)['councils']
    
    # Load the full council database
    with open('data/councils_full.json', 'r') as f:
        all_councils = json.load(f)['councils']
    
    # Create lookup by council name
    council_lookup = {c['council_name']: c for c in all_councils}
    
    print("Current Setup Analysis")
    print("="*60)
    
    # Check which councils we already have working
    print("\nOriginal councils and their platforms:")
    for council in original_councils:
        full_info = council_lookup.get(council['name'])
        if full_info:
            platform = full_info['platform']
            print(f"- {council['name']}: {platform}")
            if council['name'] == 'City of Melbourne':
                print(f"  ✓ Custom scraper working")
            elif council['name'] == 'Darebin City Council':
                print(f"  ✓ Generic scraper working (using CMS page)")
    
    # Identify similar councils
    print("\n\nCouncils using same platforms as working ones:")
    
    # Melbourne uses permeeting
    permeeting_councils = [c for c in all_councils if c['platform'] == 'permeeting']
    print(f"\nPer-meeting councils (like Melbourne): {len(permeeting_councils)}")
    for c in permeeting_councils:
        print(f"  - {c['council_name']} ({c['council_id']})")
    
    # Suggest next steps
    print("\n\nRecommended approach:")
    print("1. Keep Melbourne scraper as-is (working)")
    print("2. Keep Darebin using its specific 2025 URL (working)")
    print("3. Test if other per-meeting councils work with Melbourne's approach")
    print("4. Focus on CoreCMS councils that might have simple PDF lists")
    
    # Find potentially easy CoreCMS councils
    print("\n\nPotentially easy CoreCMS councils to test:")
    metro_corecms = [c for c in all_councils if c['platform'] == 'corecms' and any(word in c['council_name'] for word in ['City', 'Shire'])][:10]
    for c in metro_corecms:
        print(f"  - {c['council_name']}: {c['base_url']}")

if __name__ == "__main__":
    analyze_current_setup()
