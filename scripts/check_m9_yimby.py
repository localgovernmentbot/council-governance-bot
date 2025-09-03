"""
Check which M9 councils YIMBY Melbourne has already implemented
"""

# M9 councils
m9_councils = [
    'banyule',
    'darebin', 
    'hume',
    'melbourne',
    'merri-bek',  # formerly moreland
    'moonee_valley',
    'nillumbik',
    'whittlesea',
    'yarra'
]

# YIMBY councils we found earlier
yimby_councils = [
    'banyule.py',
    'bayside.py',
    'boroondara.py',
    'darebin.py',
    'glen_eira.py',
    'hobsons_bay.py',
    'kingston.py',
    'manningham.py',
    'maribyrnong.py',
    'melbourne.py',
    'merribek.py',
    'monash.py',
    'moonee_valley.py',
    'port_phillip.py',
    'stonnington.py',
    'whitehorse.py',
    'yarra.py'
]

# Clean up YIMBY list
yimby_clean = [c.replace('.py', '') for c in yimby_councils]

print("M9 Councils - YIMBY Coverage Analysis")
print("=" * 50)

have_scrapers = []
need_scrapers = []

for council in m9_councils:
    council_check = council
    if council == 'merri-bek':
        council_check = 'merribek'
    
    if council_check in yimby_clean:
        have_scrapers.append(council)
        print(f"✓ {council.title()} - YIMBY has scraper")
    else:
        need_scrapers.append(council)
        print(f"✗ {council.title()} - Need to build")

print(f"\nSummary:")
print(f"Have scrapers: {len(have_scrapers)}/9")
print(f"Need to build: {len(need_scrapers)}/9")
print(f"\nMissing: {', '.join(need_scrapers)}")
