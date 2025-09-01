import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import hashlib
from atproto import Client
import os

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

def scrape_melbourne_council():
    """Scrape City of Melbourne meeting documents"""
    print("🔍 Checking City of Melbourne...")
    
    url = "https://www.melbourne.vic.gov.au/about-council/committees-meetings/meeting-archive/pages/meeting-archive.aspx"
    
    try:
        response = requests.get(url, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        documents = []
        
        # Look for meeting links (this will need adjustment based on actual HTML)
        # For now, let's look for PDF links
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '.pdf' in href.lower():
                # Get the full URL
                if not href.startswith('http'):
                    href = f"https://www.melbourne.vic.gov.au{href}"
                
                title = link.get_text(strip=True)
                if title and ('agenda' in title.lower() or 'minutes' in title.lower()):
                    doc_type = 'agenda' if 'agenda' in title.lower() else 'minutes'
                    
                    # Create document info
                    doc = {
                        'url': href,
                        'title': title,
                        'type': doc_type,
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
        post_text = f"{emoji} {doc['council_name']} has published a new {doc['type']}:\n\n{doc['title']}\n\n🔗 Read more: {doc['url']}\n\n#VicCouncils #LocalGovernment #Melbourne"
        
        # Trim if too long (BlueSky has a 300 character limit)
        if len(post_text) > 300:
            # Shorten the title
            max_title_length = 300 - len(post_text) + len(doc['title']) - 3
            shortened_title = doc['title'][:max_title_length] + "..."
            post_text = f"{emoji} {doc['council_name']} has published a new {doc['type']}:\n\n{shortened_title}\n\n🔗 Read more: {doc['url']}\n\n#VicCouncils #LocalGovernment"
        
        # Connect and post
        client = Client()
        client.login(handle, password)
        client.send_post(text=post_text)
        
        print(f"✅ Posted: {doc['title']}")
        return True
        
    except Exception as e:
        print(f"❌ Error posting to BlueSky: {e}")
        return False

def main():
    """Main function to run the scraper"""
    print("🏛️ LocalGovernmentBot - Council Document Scanner")
    print("=" * 50)
    
    # Load data
    councils = load_councils()
    posted_docs = load_posted_documents()
    
    # Get existing hashes
    posted_hashes = {doc['hash'] for doc in posted_docs}
    
    # Scrape councils
    new_documents = []
    
    # For now, just scrape Melbourne
    melbourne_docs = scrape_melbourne_council()
    
    # Filter out already posted documents
    for doc in melbourne_docs:
        if doc['hash'] not in posted_hashes:
            new_documents.append(doc)
    
    print(f"\n📊 Found {len(new_documents)} new document(s)")
    
    # Post new documents
    for doc in new_documents[:3]:  # Limit to 3 posts per run to avoid spamming
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
    
    print("\n✅ Scan complete!")

if __name__ == "__main__":
    main()