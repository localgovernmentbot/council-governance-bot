import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import hashlib
from atproto import Client
import os
import re
import sys

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
    # Look for patterns like "25 August 2025"
    date_match = re.search(r'(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})', text, re.IGNORECASE)
    if date_match:
        return date_match.group(0)
    
    # Look for patterns like AUG25, JUL25, etc.
    date_match = re.search(r'(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\d{2}', text.upper())
    if date_match:
        return date_match.group(0)
    
    return ""

def parse_date_for_sorting(date_str):
    """Convert date string to sortable format"""
    if not date_str:
        return ""
    
    # Try to parse full dates like "25 August 2025"
    try:
        dt = datetime.strptime(date_str, "%d %B %Y")
        return dt.strftime("%Y%m%d")
    except:
        pass
    
    # Try to parse short dates like "AUG25"
    months = {'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04', 
              'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08',
              'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'}
    
    match = re.match(r'([A-Z]{3})(\d{2})', date_str)
    if match:
        month = months.get(match.group(1), '00')
        year = '20' + match.group(2)
        return f"{year}{month}01"
    
    return ""

def clean_title(title):
    """Clean up document titles"""
    # Remove file size info like (PDF, 115MB) or pdf 185.57 KB
    title = re.sub(r'\(PDF,\s*[\d\.]+\s*(KB|MB|GB)\)', '', title).strip()
    title = re.sub(r'pdf\s+[\d\.]+\s*(KB|MB|GB)', '', title, flags=re.IGNORECASE).strip()
    # Remove .pdf extension if present
    title = re.sub(r'\.pdf$', '', title, flags=re.IGNORECASE).strip()
    return title

def validate_document(doc):
    """Validate that a document is actually a meeting document"""
    title_lower = doc['title'].lower()
    
    # Exclude documents that aren't actual meeting docs
    exclude_keywords = [
        'governance rules',
        'petition sample',
        'meeting procedure',
        'how to',
        'guide',
        'template',
        'form',
        'application',
        'policy',
        'strategy',
        'annual report'
    ]
    
    if any(keyword in title_lower for keyword in exclude_keywords):
        return False
    
    # Must have date info or clear meeting reference
    if not doc.get('date_info') and not any(word in title_lower for word in ['meeting', 'council']):
        return False
    
    return True

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
                
                # Clean up the title
                title = clean_title(title)
                
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
                    'sort_date': parse_date_for_sorting(date_info),
                    'council_id': 'melbourne',
                    'council_name': 'City of Melbourne',
                    'found_date': datetime.now().isoformat()
                }
                
                # Create hash
                doc['hash'] = create_document_hash(href, title, 'melbourne')
                
                # Validate document
                if validate_document(doc):
                    documents.append(doc)
                    print(f"  Found: {title}")
                else:
                    print(f"  Skipped (not meeting doc): {title}")
        
        return documents
        
    except Exception as e:
        print(f"❌ Error scraping Melbourne: {e}")
        return []

def scrape_wyndham_council():
    """Scrape Wyndham City Council meeting documents"""
    print("🔍 Checking Wyndham City Council...")
    
    url = "https://www.wyndham.vic.gov.au/about-council/your-council/council-and-committee-meetings/council-planning-committee-contracts"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        documents = []
        
        # Look for all PDF links
        pdf_links = soup.find_all('a', href=lambda x: x and '.pdf' in x.lower())
        
        for link in pdf_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Skip if not a meeting document
            if text.lower() in ['view agenda', 'view minutes']:
                # Extract date from URL (e.g., /2021-12/ or /2022-01/)
                date_match = re.search(r'/(\d{4})-(\d{2})/', href)
                if date_match:
                    year = date_match.group(1)
                    month_num = date_match.group(2)
                    
                    # Convert to month name
                    months = ['January', 'February', 'March', 'April', 'May', 'June',
                              'July', 'August', 'September', 'October', 'November', 'December']
                    try:
                        month_name = months[int(month_num) - 1]
                        date_info = f"{month_name} {year}"
                    except:
                        date_info = f"{year}-{month_num}"
                    
                    # Determine document type
                    doc_type = 'agenda' if 'agenda' in text.lower() else 'minutes'
                    
                    # Create title with date
                    title = f"Council Meeting {text} - {date_info}"
                    
                    # Make URL absolute
                    if not href.startswith('http'):
                        href = "https://www.wyndham.vic.gov.au" + href
                    
                    # Create document info
                    doc = {
                        'url': href,
                        'title': title,
                        'type': doc_type,
                        'date_info': date_info,
                        'sort_date': f"{year}{month_num}01",
                        'council_id': 'wyndham',
                        'council_name': 'Wyndham City Council',
                        'found_date': datetime.now().isoformat()
                    }
                    
                    # Create hash
                    doc['hash'] = create_document_hash(href, title, 'wyndham')
                    
                    documents.append(doc)
                    print(f"  Found: {title}")
        
        if not documents:
            print(f"  No valid meeting documents found")
        
        return documents
        
    except Exception as e:
        print(f"❌ Error scraping Wyndham: {e}")
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
                
                # Clean title
                text = clean_title(text)
                
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
                    'sort_date': parse_date_for_sorting(date_info),
                    'council_id': council['id'],
                    'council_name': council['name'],
                    'found_date': datetime.now().isoformat()
                }
                
                # Create hash
                doc['hash'] = create_document_hash(href, text, council['id'])
                
                # Validate document
                if validate_document(doc):
                    documents.append(doc)
                    print(f"  Found: {text[:60]}...")
                else:
                    print(f"  Skipped (not meeting doc): {text[:60]}...")
        
        if not documents:
            print(f"  No valid meeting documents found")
        
        return documents
        
    except Exception as e:
        print(f"❌ Error scraping {council['name']}: {e}")
        return []

def post_to_bluesky(doc, test_mode=False):
    """Post a document to BlueSky"""
    # Create post text
    emoji = "📋" if doc['type'] == 'agenda' else "📝"
    
    # Add date info if available
    date_str = f" ({doc['date_info']})" if doc.get('date_info') else ""
    
    # Create hashtag from council ID
    council_hashtag = f"#{doc['council_id'].replace('-', '').title()}"
    
    # Start with a shorter format to avoid truncation
    post_text = f"{emoji} {doc['council_name']} - new {doc['type']}{date_str}:\n\n{doc['title']}\n\n🔗 {doc['url']}\n\n#M9Councils {council_hashtag}"
    
    # If still too long, trim the title
    if len(post_text) > 300:
        # Calculate available space for title
        base_text = f"{emoji} {doc['council_name']} - new {doc['type']}{date_str}:\n\n\n\n🔗 {doc['url']}\n\n#M9Councils {council_hashtag}"
        available_space = 300 - len(base_text) - 3  # 3 for "..."
        
        if available_space > 20:
            shortened_title = doc['title'][:available_space] + "..."
            post_text = f"{emoji} {doc['council_name']} - new {doc['type']}{date_str}:\n\n{shortened_title}\n\n🔗 {doc['url']}\n\n#M9Councils {council_hashtag}"
    
    if test_mode:
        print(f"\n🧪 TEST MODE - Would post:")
        print(f"   Title: {doc['title']}")
        print(f"   Type: {doc['type']}")
        print(f"   Date: {doc['date_info']}")
        print(f"   Council: {doc['council_name']}")
        print(f"   URL: {doc['url']}")
        print(f"   Post length: {len(post_text)} chars")
        print(f"   Post preview:")
        print("   " + "-" * 40)
        print(f"   {post_text}")
        print("   " + "-" * 40)
        return True
    
    handle = os.environ.get('BLUESKY_HANDLE')
    password = os.environ.get('BLUESKY_PASSWORD')
    
    if not handle or not password:
        print("❌ Missing BlueSky credentials!")
        return False
    
    try:
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
    # Check for test mode
    test_mode = '--test' in sys.argv
    
    print("🏛️ LocalGovernmentBot - M9 Council Scanner")
    if test_mode:
        print("🧪 RUNNING IN TEST MODE - No posts will be made")
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
        elif council['id'] == 'wyndham':
            docs = scrape_wyndham_council()
        else:
            docs = scrape_generic_council(council)
        
        # Filter out already posted documents
        for doc in docs:
            if doc['hash'] not in posted_hashes:
                all_new_documents.append(doc)
    
    print(f"\n📊 Found {len(all_new_documents)} new document(s) across all councils")
    
    if len(all_new_documents) == 0:
        print("No new documents to post.")
        return
    
    # Sort by date (newest first)
    all_new_documents.sort(key=lambda x: x.get('sort_date', ''), reverse=True)
    
    # Show summary in test mode
    if test_mode and len(all_new_documents) > 5:
        print(f"\n📋 Document summary (showing 5 of {len(all_new_documents)}):")
        print("   Newest documents will be posted first")
    
    # Post new documents (limit to 5 per run to avoid spamming)
    posted_count = 0
    for doc in all_new_documents[:5]:
        if post_to_bluesky(doc, test_mode=test_mode):
            if not test_mode:
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
        if test_mode:
            print(f"\n🧪 Would have posted {posted_count} document(s)")
        else:
            print(f"\n📮 Posted {posted_count} new document(s)")
    
    print("\n✅ Scan complete!")

if __name__ == "__main__":
    main()