"""
PDF Text Extraction for M9 Council Documents
Extracts text from council PDFs for AI summarization
"""

import requests
import PyPDF2
from io import BytesIO
import re
from typing import Optional, List


class PDFExtractor:
    """Extract text from council meeting PDFs"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def download_pdf(self, url: str) -> Optional[bytes]:
        """Download PDF from URL"""
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"Error downloading PDF from {url}: {e}")
            return None
    
    def extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """Extract text from PDF content"""
        try:
            pdf_file = BytesIO(pdf_content)
            # Suppress noisy warnings and use non-strict mode for imperfect PDFs
            try:
                import warnings
                warnings.filterwarnings("ignore", category=UserWarning)
            except Exception:
                pass
            pdf_reader = PyPDF2.PdfReader(pdf_file, strict=False)
            
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
            
            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""

    def extract_toc_lines(self, text: str, max_lines: int = 500) -> list:
        """Extract agenda/minutes item lines from the document's Table of Contents.

        Strategy:
        - Look at the first ~max_lines lines only (TOC is early in most council PDFs).
        - Start scanning after encountering a line containing the word "Agenda" (case-insensitive),
          falling back to start if not found.
        - Include only one-level-down items like "12.1 Title" or "Item 12.1 Title" (require a dot in the number).
        - Exclude generic top-level headings like "12 A VIBRANT AND THRIVING COMMUNITY" (integer only).
        - Strip dot leaders and page numbers at the end of lines.
        - Skip all-uppercase headings and common boilerplate entries.
        """
        if not text:
            return []

        raw_lines = text.split('\n')[:max_lines]
        lines = [l.strip() for l in raw_lines]

        # Find a plausible starting point after the word "Agenda"
        start_idx = 0
        for i, l in enumerate(lines[:120]):  # look in first ~120 lines for a heading
            if 'agenda' in l.lower():
                start_idx = i
                break

        scan_slice = lines[start_idx:start_idx + 350]

        toc = []
        # Require a dotted number (e.g., 12.1 or 3.4.2). Allow optional leading "Item".
        dotted_item_re = re.compile(r"^(?:Item\s+)?\d+\.\d+(?:\.\d+)?\s+.+", re.I)
        # Common boilerplate to skip if appears right after numbering
        boilerplate = [
            'apologies',
            'acknowledgement of',
            'acknowledgment of',
            'declarations of', 'conflict of interest',
            'confirmation of minutes', 'adoption of minutes',
            'public question', 'public questions', 'petitions', 'presentations',
            'business', 'urgent business', 'confidential', 'meeting closed',
            'general business', 'notices of motion', 'reports by councillors'
        ]

        def is_all_caps(s: str) -> bool:
            letters = ''.join(ch for ch in s if ch.isalpha())
            return bool(letters) and letters.upper() == letters

        for line in scan_slice:
            if not line or len(line) < 6:
                continue
            if not dotted_item_re.match(line):
                continue

            # Remove dot leaders / page numbers at end (e.g., "........ 12")
            cleaned = re.sub(r"[\.·\s]{2,}\s*\d+$", "", line).strip()

            # Basic guards
            if is_all_caps(cleaned):
                continue
            low = cleaned.lower()
            if any(low.startswith(k) or f" {k}" in low for k in boilerplate):
                continue
            # Extract title portion after the number token
            # e.g., "12.1 Title - more" -> title_part="Title - more"
            try:
                title_part = cleaned.split(None, 1)[1]
                # Remove a leading dash/colon if present
                title_part = re.sub(r"^[-–:]+\s*", "", title_part).strip()
            except Exception:
                title_part = cleaned

            # Require some lowercase letters (avoid section headers)
            if not any(ch.islower() for ch in title_part):
                continue
            # Require at least two words in the title
            if len([w for w in re.split(r"\s+", title_part) if w]) < 2:
                continue

            if 10 <= len(cleaned) <= 180:
                toc.append(cleaned)

        return toc
    
    def extract_agenda_items(self, text: str) -> List[dict]:
        """Extract individual agenda items from text"""
        items = []
        
        # Common patterns for agenda items
        patterns = [
            r'(\d+\.?\d*)\s+([^\n]+)',  # 1. Item or 1.1 Item
            r'Item\s+(\d+)\s*[-–]\s*([^\n]+)',  # Item 1 - Description
            r'Motion\s+(\d+)\s*[-–]\s*([^\n]+)',  # Motion 1 - Description
        ]
        
        # Find sections that might be agenda items
        lines = text.split('\n')
        current_item = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Check if this is an agenda item
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    # Save previous item if exists
                    if current_item:
                        items.append(current_item)
                    
                    # Start new item
                    current_item = {
                        'number': match.group(1),
                        'title': match.group(2).strip(),
                        'content': []
                    }
                    break
            else:
                # Add content to current item
                if current_item and len(line) > 20:  # Skip very short lines
                    current_item['content'].append(line)
        
        # Save last item
        if current_item:
            items.append(current_item)
        
        return items
    
    def extract_significant_sections(self, text: str) -> dict:
        """Extract sections that might be significant for public interest"""
        
        sections = {
            'financial': [],
            'planning': [],
            'community': [],
            'environmental': [],
            'policy': []
        }
        
        # Keywords for each category
        keywords = {
            'financial': ['budget', 'expenditure', 'cost', 'funding', 'grant', 'fee', 'rate', '$'],
            'planning': ['planning', 'development', 'permit', 'zoning', 'heritage', 'building'],
            'community': ['community', 'consultation', 'service', 'facility', 'program', 'event'],
            'environmental': ['environment', 'climate', 'sustainability', 'tree', 'waste', 'energy'],
            'policy': ['policy', 'strategy', 'framework', 'guideline', 'procedure', 'amendment']
        }
        
        # Split into paragraphs
        paragraphs = text.split('\n\n')
        
        for para in paragraphs:
            para_lower = para.lower()
            
            # Check each category
            for category, words in keywords.items():
                if any(word in para_lower for word in words):
                    # Extract key info
                    if len(para) > 50 and len(para) < 1000:  # Reasonable paragraph size
                        sections[category].append(para.strip())
        
        return sections
    
    def process_document(self, url: str) -> dict:
        """Main method to process a council document"""
        print(f"Processing: {url}")
        
        # Download PDF
        pdf_content = self.download_pdf(url)
        if not pdf_content:
            return {'error': 'Failed to download PDF'}
        
        # Extract text
        text = self.extract_text_from_pdf(pdf_content)
        if not text:
            return {'error': 'Failed to extract text from PDF'}
        
        # Extract structured information
        result = {
            'url': url,
            'total_length': len(text),
            'agenda_items': self.extract_agenda_items(text),
            'significant_sections': self.extract_significant_sections(text),
            'full_text': text[:5000]  # First 5000 chars for context
        }
        
        return result


# Test the extractor
if __name__ == "__main__":
    extractor = PDFExtractor()
    
    # Test with a sample document
    test_url = "https://www.darebin.vic.gov.au/-/media/Council/Files/About-Council/Council-Meetings/Agendas-and-Minutes/2025/25-February/Council-Meeting-Agenda---25-February-2025.pdf"
    
    print("Testing PDF Extractor...")
    print("=" * 60)
    
    result = extractor.process_document(test_url)
    
    if 'error' not in result:
        print(f"\nDocument processed successfully!")
        print(f"Text length: {result['total_length']} characters")
        print(f"Agenda items found: {len(result['agenda_items'])}")
        
        # Show significant sections
        print("\nSignificant sections found:")
        for category, sections in result['significant_sections'].items():
            if sections:
                print(f"  {category.title()}: {len(sections)} sections")
    else:
        print(f"Error: {result['error']}")
