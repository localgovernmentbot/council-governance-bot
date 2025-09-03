"""
Compare YIMBY councils with our full list to identify gaps
"""

import json

# YIMBY's councils (from their directory listing)
yimby_councils = [
    'banyule', 'bayside', 'boroondara', 'darebin', 'glen_eira',
    'hobsons_bay', 'kingston', 'manningham', 'maribyrnong', 'melbourne',
    'merribek', 'monash', 'moonee_valley', 'port_phillip', 'stonnington',
    'whitehorse', 'yarra'
]

# Load our full council list
with open('data/councils_full.json', 'r') as f:
    data = json.load(f)
    all_councils = data['councils']

# Find councils YIMBY doesn't have
missing_councils = []
for council in all_councils:
    council_name_lower = council['council_name'].lower().replace(' city', '').replace(' shire', '').replace(' ', '_')
    
    # Handle special cases
    if council_name_lower == 'merri-bek':
        council_name_lower = 'merribek'
    
    if council_name_lower not in yimby_councils:
        missing_councils.append({
            'id': council['council_id'],
            'name': council['council_name'],
            'platform': council['platform'],
            'url': council['base_url']
        })

# Summary by platform
platform_counts = {}
for council in missing_councils:
    platform = council['platform']
    platform_counts[platform] = platform_counts.get(platform, 0) + 1

print("Councils YIMBY doesn't have:")
print("=" * 60)
print(f"Total missing: {len(missing_councils)}")
print(f"\nBy platform:")
for platform, count in sorted(platform_counts.items()):
    print(f"  {platform}: {count}")

print(f"\nFirst 20 missing councils:")
for council in missing_councils[:20]:
    print(f"\n{council['name']} ({council['id']})")
    print(f"  Platform: {council['platform']}")
    print(f"  URL: {council['url']}")
