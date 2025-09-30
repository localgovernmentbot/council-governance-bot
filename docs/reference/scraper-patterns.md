# Council Scraper Patterns (Learned from YIMBY Project)

Documented patterns and approaches that work well for Victorian council websites.

## Common Patterns

### 1. Date Extraction

**Pattern**: Use regex with fuzzy parsing fallback

```python
import re
from dateutil.parser import parse as parse_date

# Common Australian date formats
DATE_REGEX = re.compile(
    r'\b(\d{1,2})\s(January|February|March|April|May|June|July|August|September|October|November|December)\s(\d{4})\b',
    re.IGNORECASE
)

date_text = "Council Meeting 15 October 2024"
date_match = DATE_REGEX.search(date_text)
if date_match:
    date_str = date_match.group()  # "15 October 2024"
    parsed_date = parse_date(date_str).date()
```

### 2. Time Extraction

**Pattern**: Flexible time regex with optional AM/PM

```python
TIME_REGEX = re.compile(r'\b(\d{1,2}):(\d{2})\s?(am|pm|AM|PM)?\b')

time_text = "Meeting starts at 6:30 pm"
time_match = TIME_REGEX.search(time_text)
if time_match:
    time_str = time_match.group()  # "6:30 pm"
```

### 3. PDF Link Finding

**Pattern**: BeautifulSoup with flexible regex

```python
from bs4 import BeautifulSoup
import re

# Match "agenda" in any case, anywhere in filename
AGENDA_HREF_REGEX = re.compile(r'(.*)agenda(.*)\.pdf', re.IGNORECASE)

soup = BeautifulSoup(html, 'html.parser')
agenda_link = soup.find('a', href=AGENDA_HREF_REGEX)
if agenda_link:
    pdf_url = base_url + agenda_link['href']
```

### 4. Future Meeting Filtering

**Pattern**: Parse dates and compare with today

```python
import datetime
from dateutil.parser import parse as parse_date

def is_future_meeting(element):
    text = element.get_text(separator=" ")
    date_match = DATE_REGEX.search(text)
    if not date_match:
        return False
    
    parsed_date = parse_date(date_match.group()).date()
    return parsed_date >= datetime.datetime.now().date()

# Filter meeting links
future_meetings = [
    link for link in all_links 
    if is_future_meeting(link)
]
```

### 5. Selenium for JavaScript Pages

**Pattern**: Headless Chrome with explicit waits

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

def setup_selenium():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=chrome_options)

driver = setup_selenium()
driver.get(url)

# Wait for specific element if needed
# WebDriverWait(driver, 10).until(
#     EC.presence_of_element_located((By.ID, "element-id"))
# )

html = driver.page_source
driver.quit()
```

### 6. Default Values

**Pattern**: Provide sensible defaults for missing data

```python
class CouncilScraper:
    def __init__(self):
        self.default_name = "Council Meeting"
        self.default_time = "18:00"  # 6pm is common
        self.default_location = "Council Chambers"
    
    def add_defaults(self, data):
        if not data.get('name'):
            data['name'] = self.default_name
        if not data.get('time'):
            data['time'] = self.default_time
        return data
```

## Common Victorian Council Platforms

### InfoCouncil Platform

Many councils use InfoCouncil. Pattern:

- URL structure: `/Open/YYYY/MM_DD/` or variations
- Meeting table: `<table id="grdMenu">`
- PDF links: `class="bpsGridPDFLink"`
- Date/time: `class="bpsGridDate"`

```python
soup = BeautifulSoup(html, 'html.parser')
meeting_table = soup.find('table', id='grdMenu')
first_meeting = meeting_table.find('tbody').find_all('tr')[0]
pdf_link = first_meeting.find('a', class_='bpsGridPDFLink')['href']
```

### Modern.gov

Some councils use Modern.gov:

- API endpoints available
- JSON responses
- Structured data

### Custom WordPress/CMS

Most challenging - need custom scrapers:

- Inspect network tab for API calls
- Look for JSON endpoints
- Check for PDF links in standard WordPress classes
- Use Selenium if heavy JavaScript

## Error Handling Patterns

### 1. Graceful Degradation

```python
def safe_extract(element, selector, attribute=None, default=None):
    try:
        found = element.select_one(selector)
        if not found:
            return default
        if attribute:
            return found.get(attribute, default)
        return found.get_text(strip=True)
    except Exception as e:
        logger.warning(f"Extraction failed: {e}")
        return default
```

### 2. Multiple Fallback Strategies

```python
def find_pdf_link(soup):
    # Strategy 1: Look for "agenda" in link text
    for link in soup.find_all('a'):
        if 'agenda' in link.get_text().lower():
            if link.get('href', '').endswith('.pdf'):
                return link['href']
    
    # Strategy 2: Look for PDF icon or class
    pdf_link = soup.find('a', class_='pdf-download')
    if pdf_link:
        return pdf_link['href']
    
    # Strategy 3: Any PDF link
    pdf_link = soup.find('a', href=re.compile(r'\.pdf$'))
    if pdf_link:
        return pdf_link['href']
    
    return None
```

## Testing Approach

### Cache Responses

Save HTML responses for testing:

```python
import json
from pathlib import Path

def save_test_case(council_name, html, result):
    test_dir = Path('tests/test-cases')
    test_dir.mkdir(exist_ok=True)
    
    # Save HTML
    with open(test_dir / f'{council_name}-replay_data.json', 'w') as f:
        json.dump({'html': html}, f)
    
    # Save expected result
    with open(test_dir / f'{council_name}-result.json', 'w') as f:
        json.dump(result, f)
```

This allows:
- Fast testing without hitting council websites
- Reproducible tests
- Easier debugging

## Best Practices

1. **Always use user agents** - Some councils block default Python requests
2. **Respect robots.txt** - Check allowed paths
3. **Rate limit** - Add delays between requests
4. **Log extensively** - Helps debug when scrapers break
5. **Handle missing data gracefully** - Councils update websites frequently
6. **Test regularly** - Websites change, scrapers break
7. **Document URL patterns** - Future you will thank you

## Common Failures and Solutions

| Problem | Solution |
|---------|----------|
| 403 Forbidden | Add proper user agent, check robots.txt |
| Empty results | Check if JavaScript renders content (use Selenium) |
| Wrong meeting scraped | Add date filtering, check meeting type |
| PDF link 404s | URL might be relative, join with base_url |
| Date parsing fails | Use fuzzy parsing with dateutil |
| Intermittent failures | Add retries with exponential backoff |

---

*Based on patterns learned from YIMBY Melbourne council-meeting-agenda-scraper project*
