import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import hashlib
from atproto import Client
import os
import re

def load_councils():
    """Load the list of councils from our JSON file"""
    with open('data/councils.json', 'r') as f:
        return json.load(f)['councils']

def load_posted_documents():
    """Load the list of already posted documents"""
    with open('data/posted.json', 'r') as f:
        return json.load(f)['posted_documents']

def save_posted_documents(posted_docs):
    """Save the updated list of posted documents"""
    with open('data/posted.json', 'w') as f:
        json.dump({'posted_documents': posted_docs}, f, indent=2)

def create_document_hash(url, title, council_id):
    """Create a unique hash for a document"""
    content = f"{url}|{title}|{council_id}"
    return hashlib.md5(content.encode()).hexdigest()

def extract_date_info(text):
    """Extract date information from text"""
    # Look for patterns like AUG25, JUL25, etc.
    date_match = re.search(r'(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\d{2}', text.upper())
    if date_match:
        return date_match.group(0)
    # Look for patterns like "26 August 2025"
    date_match = re.search(r'\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}', text, re.IGNORECASE)
    if date_match:
        return date_match.group(0)
    return ""

def scrape_melbourne_council():
    """Scrape City of Melbourne meeting documents"""
    print("🔍 Checking City of Melbourne...")
    
    url = "https://www.melbourne.vic.gov.au/about-council/committees-meetings/meeting-archive/pages/meeting-archive.aspx"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        documents = []
        
        # Look for all links
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            href = link.get('href', '')
            # Look for PDF links from the S3 bucket
            if '.pdf' in href.lower() and 's3.ap-southeast-4.amazonaws.com' in href:
                title = link.get_text(strip=True)
                
                # Clean up the title (remove file size info)
                title = re.sub(r'pdf\s+[\d\.]+\s*(KB|MB)', '', title).strip()
                
                # Determine document type
                doc_type = None
                if 'MINUTES' in title.upper():
                    doc_type = 'minutes'
                elif 'AGENDA' in title.upper():
                    doc_type = 'agenda'
                else:
                    # Skip non-meeting documents
                    continue
                
                # Extract date info
                date_info = extract_date_info(title)
                
                # Create document info
                doc = {
                    'url': href,
                    'title': title,
                    'type': doc_type,
                    'date_info': date_info,
                    'council_id': 'melbourne',
                    'council_name': 'City of Melbourne',
                    'found_date': datetime.now().isoformat()
                }
                
                # Create hash
                doc['hash'] = create_document_hash(href, title, 'melbourne')
                
                documents.append(doc)
                print(f"  Found: {title}")
        
        return documents
        
    except Exception as e:
        print(f"❌ Error scraping Melbourne: {e}")
        return []

def scrape_generic_council(council):
    """Generic scraper for councils with standard PDF links"""
    print(f"🔍 Checking {council['name']}...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(council['meetings_url'], headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"  ⚠️  Got status code {response.status_code}")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        documents = []
        
        # Look for all links
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Look for PDF links with meeting-related keywords
            if '.pdf' in href.lower() and any(keyword in text.lower() for keyword in ['agenda', 'minutes']):
                # Make URL absolute
                if not href.startswith('http'):
                    if href.startswith('/'):
                        href = council['url'] + href
                    else:
                        href = council['url'] + '/' + href
                
                # Determine document type
                doc_type = 'minutes' if 'minutes' in text.lower() else 'agenda'
                
                # Extract date info
                date_info = extract_date_info(text)
                
                # Create document info
                doc = {
                    'url': href,
                    'title': text,
                    'type': doc_type,
                    'date_info': date_info,
                    'council_id': council['id'],
                    'council_name': council['name'],
                    'found_date': datetime.now().isoformat()
                }
                
                # Create hash
                doc['hash'] = create_document_hash(href, text, council['id'])
                
                documents.append(doc)
                print(f"  Found: {text[:60]}...")
        
        if not documents:
            print(f"  No PDF documents found")
        
        return documents
        
    except Exception as e:
        print(f"❌ Error scraping {council['name']}: {e}")
        return []

def post_to_bluesky(doc):
    """Post a document to BlueSky"""
    handle = os.environ.get('BLUESKY_HANDLE')
    password = os.environ.get('BLUESKY_PASSWORD')
    
    if not handle or not password:
        print("❌ Missing BlueSky credentials!")
        return False
    
    try:
        # Create post text
        emoji = "📋" if doc['type'] == 'agenda' else "📝"
        
        # Add date info if available
        date_str = f" ({doc['date_info']})" if doc.get('date_info') else ""
        
        # Create hashtag from council ID
        council_hashtag = f"#{doc['council_id'].replace('-', '').title()}"
        
        post_text = f"{emoji} {doc['council_name']} has published new {doc['type']}{date_str}:\n\n{doc['title']}\n\n🔗 View: {doc['url']}\n\n#M9Councils #VicCouncils {council_hashtag}"
        
        # Trim if too long (BlueSky has a 300 character limit)
        if len(post_text) > 300:
            # Calculate how much we need to trim
            excess = len(post_text) - 297  # Leave room for "..."
            # Trim the title
            title_max = len(doc['title']) - excess
            if title_max > 10:  # Keep at least 10 chars of title
                shortened_title = doc['title'][:title_max] + "..."
                post_text = f"{emoji} {doc['council_name']} - new {doc['type']}{date_str}:\n\n{shortened_title}\n\n🔗 {doc['url']}\n\n#M9Councils {council_hashtag}"
        
        # Connect and post
        client = Client()
        client.login(handle, password)
        client.send_post(text=post_text)
        
        print(f"✅ Posted: {doc['title'][:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ Error posting to BlueSky: {e}")
        return False

def main():
    """Main function to run the scraper"""
    print("🏛️ LocalGovernmentBot - M9 Council Scanner")
    print("=" * 50)
    
    # Load data
    councils = load_councils()
    posted_docs = load_posted_documents()
    
    # Get existing hashes
    posted_hashes = {doc['hash'] for doc in posted_docs}
    
    # Scrape all councils
    all_new_documents = []
    
    for council in councils:
        if council.get('scraper') == 'melbourne_scraper':
            docs = scrape_melbourne_council()
        else:
            docs = scrape_generic_council(council)
        
        # Filter out already posted documents
        for doc in docs:
            if doc['hash'] not in posted_hashes:
                all_new_documents.append(doc)
    
    print(f"\n📊 Found {len(all_new_documents)} new document(s) across all councils")
    
    # Post new documents (limit to 5 per run to avoid spamming)
    posted_count = 0
    for doc in all_new_documents[:5]:
        if post_to_bluesky(doc):
            # Add to posted documents
            posted_docs.append({
                'hash': doc['hash'],
                'council': doc['council_id'],
                'type': doc['type'],
                'title': doc['title'],
                'url': doc['url'],
                'posted_at': datetime.now().isoformat()
            })
            
            # Save after each successful post
            save_posted_documents(posted_docs)
            posted_count += 1
    
    if posted_count > 0:
        print(f"\n📮 Posted {posted_count} new document(s)")
    
    print("\n✅ Scan complete!")

if __name__ == "__main__":
    main()