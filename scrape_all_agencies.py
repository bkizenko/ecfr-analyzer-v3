#!/usr/bin/env python3
import requests
import json
import re
import time
import random
import os

# Browser headers to mimic a real browser
BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0'
}

def random_delay(min_sec=1.5, max_sec=3.0):
    """Add a delay between requests to avoid being rate-limited"""
    delay = random.uniform(min_sec, max_sec)
    print(f"Waiting {delay:.2f} seconds...")
    time.sleep(delay)

def get_main_agencies():
    """Get the list of main agencies from the homepage"""
    try:
        response = requests.get('https://cfr-metrics.com/', headers=BROWSER_HEADERS)
        response.raise_for_status()
        
        # Create agencies directory if it doesn't exist
        if not os.path.exists('agencies'):
            os.makedirs('agencies')
        
        # Save the homepage HTML
        with open('agencies/homepage.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print("Homepage saved to agencies/homepage.html")
        
        # Extract agency slugs using regex
        agency_links = re.findall(r'href="/agency/([^"]+)"', response.text)
        
        # Remove duplicates
        agency_slugs = list(set(agency_links))
        
        print(f"Found {len(agency_slugs)} main agencies")
        
        # Save the agency slugs to a file
        with open('agencies/main_agency_slugs.json', 'w') as f:
            json.dump(agency_slugs, f, indent=2)
        
        print("Main agency slugs saved to agencies/main_agency_slugs.json")
        
        return agency_slugs
    
    except Exception as e:
        print(f"Error getting main agencies: {e}")
        return []

def scrape_agency_page(agency_slug):
    """Scrape data for a single agency"""
    url = f'https://cfr-metrics.com/agency/{agency_slug}'
    
    try:
        print(f"Fetching data for agency: {agency_slug}")
        response = requests.get(url, headers=BROWSER_HEADERS)
        response.raise_for_status()
        
        # Save the HTML file
        filename = f'agencies/agency_{agency_slug}.html'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"Agency HTML saved to {filename}")
        
        # Extract agency metrics data
        agency_metrics = extract_agency_metrics(response.text)
        
        if agency_metrics:
            # Save the metrics data to a JSON file
            metrics_filename = f'agencies/metrics_{agency_slug}.json'
            with open(metrics_filename, 'w') as f:
                json.dump(agency_metrics, f, indent=2)
            
            print(f"Agency metrics saved to {metrics_filename}")
            
            # Get the agency name
            agency_name = extract_agency_name(response.text)
            
            return {
                'slug': agency_slug,
                'name': agency_name,
                'inner_agencies': agency_metrics
            }
        
        return None
    
    except Exception as e:
        print(f"Error scraping agency {agency_slug}: {e}")
        return None

def extract_agency_name(html_content):
    """Extract the agency name from the HTML"""
    name_match = re.search(r'<div class="font-title bg-primary text-light fixed left-0 right-0 top-0[^>]+>([^<]+)</div>', html_content)
    if name_match:
        return name_match.group(1).strip()
    return "Unknown Agency"

def extract_agency_metrics(html_content):
    """Extract agency metrics from the HTML"""
    # Find the agencyMetrics section in the script tag
    pattern = r'"agencyMetrics":\s*\[(.*?)\],\s*"isSubAgency"'
    match = re.search(pattern, html_content, re.DOTALL)
    
    if not match:
        print("Could not find agencyMetrics in the HTML")
        return None
    
    try:
        # Create proper JSON data
        json_data = '[' + match.group(1) + ']'
        
        # Parse the JSON data
        agency_metrics = json.loads(json_data)
        
        # Format the data for easier readability
        formatted_metrics = []
        for item in agency_metrics:
            agency_info = item.get('agency', {})
            metrics = item.get('metrics', {})
            
            formatted_metrics.append({
                'name': agency_info.get('name', 'Unknown'),
                'slug': agency_info.get('slug', ''),
                'wordCount': metrics.get('wordCount', 0),
                'sectionCount': metrics.get('sectionCount', 0),
                'cfr_reference': agency_info.get('cfr_references', [])
            })
        
        return formatted_metrics
    
    except Exception as e:
        print(f"Error parsing agency metrics: {e}")
        return None

def main():
    """Main function to scrape all agencies and their inner agencies"""
    print("Starting scrape of all agencies...")
    
    # Get the list of main agencies
    main_agencies = get_main_agencies()
    
    if not main_agencies:
        print("No main agencies found. Exiting.")
        return
    
    # Create the data directory
    if not os.path.exists('agencies_data'):
        os.makedirs('agencies_data')
    
    # Scrape each agency (limited to 5 for testing)
    all_agency_data = []
    
    for i, agency_slug in enumerate(main_agencies[:5]):  # Limit to 5 for testing
        print(f"\nProcessing agency {i+1}/{len(main_agencies[:5])}: {agency_slug}")
        
        agency_data = scrape_agency_page(agency_slug)
        
        if agency_data:
            all_agency_data.append(agency_data)
            
            # Save individual agency data
            with open(f'agencies_data/{agency_slug}.json', 'w') as f:
                json.dump(agency_data, f, indent=2)
        
        # Add a delay between requests to avoid rate limiting
        if i < len(main_agencies) - 1:
            random_delay()
    
    # Save all agency data
    with open('agencies_data/all_agencies_data.json', 'w') as f:
        json.dump(all_agency_data, f, indent=2)
    
    print("\nAll agency data saved to agencies_data/all_agencies_data.json")

if __name__ == "__main__":
    main() 