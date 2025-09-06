#!/usr/bin/env python3
"""
Monitor the status of Victorian Council Bot
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def format_time_ago(date_str):
    """Format how long ago a date was"""
    try:
        date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        diff = datetime.now() - date.replace(tzinfo=None)
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        else:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    except:
        return date_str

def main():
    print("""
╔════════════════════════════════════════════════════════════════╗
║          VICTORIAN COUNCIL BOT - STATUS MONITOR               ║
╚════════════════════════════════════════════════════════════════╝
    """)
    
    base_dir = Path(__file__).parent.parent
    
    # Check configuration
    print("\n📋 CONFIGURATION:")
    print("-" * 40)
    
    registry_file = base_dir / 'src' / 'registry' / 'all_councils.json'
    if registry_file.exists():
        with open(registry_file) as f:
            data = json.load(f)
            councils = data.get('councils', [])
        
        # Count by type
        by_type = {}
        for c in councils:
            t = c.get('type', 'unknown')
            by_type[t] = by_type.get(t, 0) + 1
        
        print(f"Councils configured: {len(councils)}")
        for t, count in sorted(by_type.items()):
            print(f"  • {t}: {count}")
    
    # Check scraping results
    print("\n📊 SCRAPING STATUS:")
    print("-" * 40)
    
    results_files = [
        ('m9_scraper_results.json', 'M9 Councils'),
        ('all_councils_results.json', 'All Councils')
    ]
    
    for file_name, label in results_files:
        results_file = base_dir / file_name
        if results_file.exists():
            with open(results_file) as f:
                data = json.load(f)
            
            scrape_date = data.get('scrape_date', 'Unknown')
            time_ago = format_time_ago(scrape_date)
            
            print(f"\n{label}:")
            print(f"  Last scrape: {time_ago}")
            print(f"  Documents found: {data.get('total_documents', 0)}")
            print(f"  Working councils: {data.get('working_councils', 0)}/{data.get('total_councils', 0)}")
            
            # Show top councils
            if 'council_stats' in data:
                working = [s for s in data['council_stats'] if s.get('working')]
                if working:
                    top = sorted(working, key=lambda x: x.get('total', 0), reverse=True)[:3]
                    print(f"  Top councils:")
                    for s in top:
                        print(f"    • {s['name']}: {s['total']} docs")
    
    # Check posting status
    print("\n📮 POSTING STATUS:")
    print("-" * 40)
    
    posted_file = base_dir / 'posted_bluesky.json'
    if posted_file.exists():
        with open(posted_file) as f:
            data = json.load(f)
        
        posts = data.get('posts', {})
        posted = data.get('posted', [])
        
        print(f"Total posts made: {len(posts)}")
        print(f"Unique documents: {len(posted)}")
        
        if posts:
            print("\nRecent posts:")
            for hash_id, post_data in list(posts.items())[-3:]:
                uri = post_data.get('uri', '')
                if 'did:plc:' in uri:
                    post_id = uri.split('/')[-1]
                    print(f"  • https://bsky.app/profile/councilbot.bsky.social/post/{post_id}")
    
    # Check environment
    print("\n⚙️ ENVIRONMENT:")
    print("-" * 40)
    
    env_file = base_dir / '.env'
    if env_file.exists():
        print("✅ Environment configured (.env exists)")
    else:
        print("⚠️  No .env file - copy .env.example to .env")
    
    # Show GitHub Actions status
    workflow_file = base_dir / '.github' / 'workflows' / 'all_councils.yml'
    if workflow_file.exists():
        print("✅ GitHub Actions workflow configured")
    else:
        print("⚠️  GitHub Actions workflow missing")
    
    print("\n" + "=" * 60)
    print("Monitor complete. Bot is ready for deployment!")
    print("\n🌐 BlueSky: https://bsky.app/profile/councilbot.bsky.social")

if __name__ == '__main__':
    main()
