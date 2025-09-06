#!/usr/bin/env python3
"""
Post one document to BlueSky as a test
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, 'src')
from bluesky_integration import BlueSkyPoster

def main():
    print("TESTING BLUESKY POSTING")
    print("=" * 60)
    
    # Load M9 results (we know these work)
    results_file = Path('m9_scraper_results.json')
    if not results_file.exists():
        print("❌ No results file found. Run m9_unified_scraper.py first")
        return
    
    with open(results_file) as f:
        data = json.load(f)
    
    if not data['documents']:
        print("❌ No documents found in results")
        return
    
    # Initialize poster
    poster = BlueSkyPoster()
    
    # Find first unposted document
    posted_count = 0
    for doc in data['documents']:
        council_name = doc['council_name']
        doc_url = doc['url']
        
        # Check if already posted
        url_hash = poster._hash_url_only(council_name, doc_url)
        
        if url_hash not in poster.posted_docs:
            # This one hasn't been posted yet!
            print(f"\nFound new document to post:")
            print(f"  Council: {council_name}")
            print(f"  Type: {doc['document_type']}")
            print(f"  Title: {doc['title'][:60]}...")
            print(f"  Date: {doc.get('date', 'N/A')}")
            print(f"  URL: {doc_url}")
            
            # Determine hashtag (simplified for M9)
            hashtag_map = {
                'Melbourne': 'Melbourne',
                'Port Phillip': 'PortPhillip',
                'Yarra': 'Yarra',
                'Stonnington': 'Stonnington',
                'Darebin': 'Darebin',
                'Merri-bek': 'Merribek',
                'Moonee Valley': 'MooneeValley',
                'Maribyrnong': 'Maribyrnong',
                'Hobsons Bay': 'HobsonsBay'
            }
            
            council_hashtag = hashtag_map.get(council_name, council_name.replace(' ', ''))
            
            print(f"\nPosting to BlueSky...")
            
            success = poster.post_document(
                council_name=council_name,
                doc_type=doc['document_type'],
                doc_title=doc['title'],
                doc_url=doc_url,
                date_str=doc.get('date'),
                council_hashtag=council_hashtag
            )
            
            if success:
                print("✅ Successfully posted to BlueSky!")
                print(f"Check: https://bsky.app/profile/councilbot.bsky.social")
                posted_count += 1
                break
            else:
                print("⚠️ Document was already posted or error occurred")
        
    if posted_count == 0:
        print("\n⚠️ All documents have already been posted")
        print(f"Total posted documents: {len(poster.posted_docs)}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")

if __name__ == '__main__':
    main()
