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
                
                # Extract date info if possible
                date_match = re.search(r'(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\d{2}', title)
                date_info = date_match.group(0) if date_match else ""
                
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
        
        post_text = f"{emoji} {doc['council_name']} has published new {doc['type']}{date_str}:\n\n{doc['title']}\n\n🔗 View: {doc['url']}\n\n#VicCouncils #LocalGovernment #Melbourne #Transparency"
        
        # Trim if too long (BlueSky has a 300 character limit)
        if len(post_text) > 300:
            # Calculate how much we need to trim
            excess = len(post_text) - 297  # Leave room for "..."
            # Trim the title
            title_max = len(doc['title']) - excess
            if title_max > 10:  # Keep at least 10 chars of title
                shortened_title = doc['title'][:title_max] + "..."
                post_text = f"{emoji} {doc['council_name']} has published new {doc['type']}{date_str}:\n\n{shortened_title}\n\n🔗 View: {doc['url']}\n\n#VicCouncils #LocalGov"
        
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