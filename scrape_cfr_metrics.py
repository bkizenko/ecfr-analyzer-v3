#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import json
import time
import random

# Browser headers to mimic a real browser
BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://cfr-metrics.com/',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
}

# Add some random delay between requests to make it look more human
def random_delay():
    delay = random.uniform(1.0, 2.5)
    print(f"Waiting {delay:.2f} seconds...")
    time.sleep(delay)

def get_agency_metrics(agency_slug):
    """Get metrics for a specific agency and its inner agencies"""
    url = f"https://cfr-metrics.com/agency/{agency_slug}"
    try:
        print(f"Fetching data from {url}")
        response = requests.get(url, headers=BROWSER_HEADERS)
        if response.status_code != 200:
            print(f"Failed to get data for {agency_slug}: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract agency name
        agency_name_elem = soup.find('div', class_='font-title text-4xl font-bold md:text-6xl')
        if not agency_name_elem:
            print(f"Could not find agency name element for {agency_slug}")
            return None
            
        agency_name = agency_name_elem.text.strip()
        print(f"Found agency: {agency_name}")
        
        # Extract metrics - word count and section count
        metrics_divs = soup.find_all('div', class_='font-title text-4xl font-bold md:text-5xl')
        if len(metrics_divs) >= 2:
            word_count = int(metrics_divs[0].find('span').text.replace(',', ''))
            section_count = int(metrics_divs[1].find('span').text.replace(',', ''))
            print(f"  Word count: {word_count:,}, Section count: {section_count:,}")
        else:
            print(f"  Could not find metrics divs (found {len(metrics_divs)})")
            word_count = 0
            section_count = 0
            
        # Get inner agencies if any
        inner_agencies = []
        inner_agency_table = soup.find('table', class_='table-auto')
        if inner_agency_table:
            rows = inner_agency_table.find_all('tr')[1:]  # Skip header row
            print(f"  Found {len(rows)} inner agencies")
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    inner_name = cols[0].text.strip()
                    inner_words = int(cols[1].text.replace(',', ''))
                    inner_sections = int(cols[2].text.replace(',', ''))
                    inner_agencies.append({
                        'name': inner_name,
                        'wordCount': inner_words,
                        'sectionCount': inner_sections
                    })
        else:
            print("  No inner agencies found")
        
        return {
            'name': agency_name,
            'wordCount': word_count,
            'sectionCount': section_count,
            'innerAgencies': inner_agencies
        }
    except Exception as e:
        print(f"Error scraping {agency_slug}: {e}")
        return None

def get_all_agencies():
    """Get the main page and extract all agencies"""
    url = "https://cfr-metrics.com/"
    print(f"Fetching main page from {url}")
    response = requests.get(url, headers=BROWSER_HEADERS)
    
    # Save the raw HTML for debugging
    with open('cfr_metrics_homepage.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print(f"Saved raw HTML to cfr_metrics_homepage.html")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Get total metrics
    metrics_divs = soup.find_all('div', class_='font-title text-4xl font-bold md:text-5xl')
    if len(metrics_divs) >= 4:
        total_words = int(metrics_divs[0].find('span').text.replace(',', ''))
        total_sections = int(metrics_divs[1].find('span').text.replace(',', ''))
        total_agencies = int(metrics_divs[2].find('span').text.replace(',', ''))
        total_inner_agencies = int(metrics_divs[3].find('span').text.replace(',', ''))
        print(f"Total Words: {total_words:,}")
        print(f"Total Sections: {total_sections:,}")
        print(f"Total Agencies: {total_agencies:,}")
        print(f"Total Inner Agencies: {total_inner_agencies:,}")
    else:
        print(f"Could not find all metric divs (found {len(metrics_divs)})")
        total_words = 0
        total_sections = 0
        total_agencies = 0
        total_inner_agencies = 0
    
    # Get agency list and their metrics
    agencies = []
    agency_items = soup.find_all('a', href=True)
    
    agency_slugs = []
    for item in agency_items:
        href = item.get('href', '')
        if href.startswith('/agency/'):
            slug = href.replace('/agency/', '')
            if slug not in agency_slugs:
                agency_slugs.append(slug)
    
    print(f"Found {len(agency_slugs)} agency slugs")
    
    # Get metrics for each agency
    for i, slug in enumerate(agency_slugs):
        print(f"Scraping {i+1}/{len(agency_slugs)}: {slug}")
        agency_data = get_agency_metrics(slug)
        if agency_data:
            agencies.append({
                'slug': slug,
                'data': agency_data
            })
            
            # Save progress after each successful agency
            with open(f'agency_{slug}.json', 'w') as f:
                json.dump(agency_data, f, indent=2)
                
        random_delay()  # Add random delay between requests
    
    return {
        'totalMetrics': {
            'wordCount': total_words,
            'sectionCount': total_sections,
            'agencyCount': total_agencies,
            'innerAgencyCount': total_inner_agencies
        },
        'agencies': agencies
    }

if __name__ == "__main__":
    print("Starting CFR metrics scraper...")
    all_data = get_all_agencies()
    
    # Save to file
    with open('cfr_metrics_data.json', 'w') as f:
        json.dump(all_data, f, indent=2)
    
    # Print summary
    print("\nSummary:")
    print(f"Total Words: {all_data['totalMetrics']['wordCount']:,}")
    print(f"Total Sections: {all_data['totalMetrics']['sectionCount']:,}")
    print(f"Total Agencies: {all_data['totalMetrics']['agencyCount']:,}")
    print(f"Total Inner Agencies: {all_data['totalMetrics']['innerAgencyCount']:,}")
    print(f"Agencies scraped: {len(all_data['agencies'])}")
    
    # Print top 10 agencies by word count
    print("\nTop 10 agencies by word count:")
    sorted_agencies = sorted(all_data['agencies'], key=lambda x: x['data']['wordCount'], reverse=True)
    for i, agency in enumerate(sorted_agencies[:10]):
        print(f"{i+1}. {agency['data']['name']}: {agency['data']['wordCount']:,} words, {agency['data']['sectionCount']:,} sections") 