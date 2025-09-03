"""
Check YIMBY scrapers for remaining M9 councils
"""

import os

# Remaining M9 councils we need
remaining_m9 = [
    'maribyrnong',
    'merribek',  # was merri-bek
    'moonee_valley',
    'port_phillip',
    'stonnington',
    'yarra'
]

yimby_path = "/Users/jonathonmarsden/Desktop/yimby-scrapers/aus_council_scrapers/scrapers/vic"

print("Checking YIMBY scrapers for remaining M9 councils:")
print("=" * 60)

for council in remaining_m9:
    file_path = os.path.join(yimby_path, f"{council}.py")
    
    if os.path.exists(file_path):
        print(f"\n✓ {council.upper()} - YIMBY scraper exists")
        
        # Check if it's implemented (not just placeholder)
        with open(file_path, 'r') as f:
            content = f.read()
            if "scraper_return = ScraperReturn(" in content:
                print("  Status: Implemented")
            elif "YOUR CODE HERE" in content:
                print("  Status: Placeholder only")
            else:
                print("  Status: Needs checking")
                
    else:
        print(f"\n✗ {council.upper()} - No YIMBY scraper")
