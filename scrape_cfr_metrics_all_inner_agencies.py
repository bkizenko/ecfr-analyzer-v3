#!/usr/bin/env python3
import requests
import json
import re
import time
import random

# Browser headers to mimic a real browser
BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://cfr-metrics.com/',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0'
}

def random_delay():
    """Add a small random delay between requests to avoid being rate-limited"""
    delay = random.uniform(1.0, 2.5)
    print(f"Waiting {delay:.2f} seconds...")
    time.sleep(delay)

def get_main_page_data():
    """Get the CFR data directly from the JavaScript on the homepage"""
    url = "https://cfr-metrics.com/"
    print(f"Fetching main page from {url}")
    
    try:
        response = requests.get(url, headers=BROWSER_HEADERS)
        if response.status_code != 200:
            print(f"Failed to get homepage: HTTP {response.status_code}")
            return None
            
        raw_html = response.text
        
        # Save the raw HTML for debugging
        with open('cfr_metrics_raw.html', 'w', encoding='utf-8') as f:
            f.write(raw_html)
        print(f"Saved raw HTML to cfr_metrics_raw.html")
        
        # Extract the main data script which contains all agencies
        script_pattern = r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>'
        script_match = re.search(script_pattern, raw_html)
        
        if not script_match:
            print("Could not find Next.js data script")
            return None
            
        script_content = script_match.group(1)
        
        try:
            # Parse the JSON data from the script
            data = json.loads(script_content)
            
            # Save the Next.js data for analysis
            with open('next_data.json', 'w') as f:
                json.dump(data, f, indent=2)
            print("Next.js data saved to next_data.json")
            
            # Extract the main page props which contains agency data
            if 'props' in data.get('props', {}).get('pageProps', {}):
                page_props = data['props']['pageProps']['props']
                
                # Extract the total metrics
                total_metrics = {
                    "totalWordCount": page_props.get('totalWordCount', 0),
                    "totalSectionCount": page_props.get('totalSectionCount', 0),
                    "totalAgencyCount": page_props.get('totalAgencyCount', 0),
                    "totalInnerAgencyCount": page_props.get('totalInnerAgencyCount', 0)
                }
                
                # Get all agencies
                agencies_data = page_props.get('agencies', [])
                
                # Process and organize the data
                agencies = []
                for agency in agencies_data:
                    agencies.append({
                        "name": agency.get('name', ''),
                        "slug": agency.get('slug', ''),
                        "wordCount": agency.get('metrics', {}).get('wordCount', 0),
                        "sectionCount": agency.get('metrics', {}).get('sectionCount', 0)
                    })
                
                # Sort agencies by word count
                agencies.sort(key=lambda x: x['wordCount'], reverse=True)
                
                return {
                    "totalMetrics": total_metrics,
                    "agencies": agencies
                }
            else:
                print("Could not find agency data in the Next.js data")
                return None
                
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return None
            
    except Exception as e:
        print(f"Error fetching main page: {e}")
        return None

def get_agency_inner_data(agency_slug):
    """Get data for a specific agency including inner agencies"""
    url = f"https://cfr-metrics.com/agency/{agency_slug}"
    print(f"Fetching data from {url}")
    
    try:
        response = requests.get(url, headers=BROWSER_HEADERS)
        if response.status_code != 200:
            print(f"Failed to get data for {agency_slug}: HTTP {response.status_code}")
            return None
            
        raw_html = response.text
        
        # Extract the agency page data script
        script_pattern = r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>'
        script_match = re.search(script_pattern, raw_html)
        
        if not script_match:
            print(f"Could not find Next.js data script for {agency_slug}")
            return None
            
        script_content = script_match.group(1)
        
        try:
            # Parse the JSON data from the script
            data = json.loads(script_content)
            
            # Get the agency data from the page props
            if 'props' in data.get('props', {}).get('pageProps', {}):
                page_props = data['props']['pageProps']['props']
                agency = page_props.get('agency', {})
                
                # Extract agency info
                agency_data = {
                    "name": agency.get('name', ''),
                    "slug": agency.get('slug', ''),
                    "wordCount": agency.get('metrics', {}).get('wordCount', 0),
                    "sectionCount": agency.get('metrics', {}).get('sectionCount', 0),
                    "innerAgencies": []
                }
                
                # Extract inner agencies
                inner_agencies = []
                for child in agency.get('children', []):
                    inner_agency = {
                        "name": child.get('name', ''),
                        "slug": child.get('slug', ''),
                        "wordCount": child.get('metrics', {}).get('wordCount', 0),
                        "sectionCount": child.get('metrics', {}).get('sectionCount', 0)
                    }
                    inner_agencies.append(inner_agency)
                
                # Sort inner agencies by word count
                inner_agencies.sort(key=lambda x: x['wordCount'], reverse=True)
                agency_data['innerAgencies'] = inner_agencies
                
                return agency_data
            else:
                print(f"Could not find agency data for {agency_slug}")
                return None
                
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON for {agency_slug}: {e}")
            return None
            
    except Exception as e:
        print(f"Error fetching {agency_slug}: {e}")
        return None

def get_all_agencies_with_inner():
    """Get all agencies and their inner agencies"""
    # First, get main page data with all agencies
    main_data = get_main_page_data()
    
    if not main_data:
        print("Failed to get main page data")
        return None
    
    total_metrics = main_data['totalMetrics']
    agencies = main_data['agencies']
    
    # Now get inner agency data for each agency
    all_agencies = []
    inner_agencies_flat = []
    
    for i, agency in enumerate(agencies):
        slug = agency['slug']
        print(f"Processing {i+1}/{len(agencies)}: {slug} ({agency['name']})")
        
        agency_data = get_agency_inner_data(slug)
        if agency_data:
            all_agencies.append(agency_data)
            
            # Add inner agencies to a flat list for easier reporting
            for inner in agency_data["innerAgencies"]:
                inner_agencies_flat.append({
                    "parentAgency": agency_data["name"],
                    "name": inner["name"],
                    "wordCount": inner["wordCount"],
                    "sectionCount": inner["sectionCount"]
                })
            
            # Save progress after each successful agency
            with open(f'agency_{slug}.json', 'w') as f:
                json.dump(agency_data, f, indent=2)
                
        random_delay()
    
    # Sort agencies and inner agencies by word count
    all_agencies.sort(key=lambda x: x["wordCount"], reverse=True)
    inner_agencies_flat.sort(key=lambda x: x["wordCount"], reverse=True)
    
    return {
        "totalMetrics": total_metrics,
        "agencies": all_agencies,
        "innerAgencies": inner_agencies_flat
    }

def print_markdown_tables(data):
    """Print the metrics in markdown format tables"""
    total = data["totalMetrics"]
    print("\n# CFR Metrics Summary")
    
    print(f"\n## Overall Totals")
    print(f"- Total Words: {total['totalWordCount']:,}")
    print(f"- Total Sections: {total['totalSectionCount']:,}")
    print(f"- Total Agencies: {total['totalAgencyCount']:,}")
    print(f"- Total Inner Agencies: {total['totalInnerAgencyCount']:,}")
    
    print("\n## Top 30 Agencies by Word Count")
    print("| Rank | Agency | Word Count | Section Count |")
    print("|------|--------|------------|---------------|")
    for i, agency in enumerate(data["agencies"][:30]):
        print(f"| {i+1} | {agency['name']} | {agency['wordCount']:,} | {agency['sectionCount']:,} |")
    
    print("\n## All Inner Agencies by Word Count")
    print("| Rank | Inner Agency | Parent Agency | Word Count | Section Count |")
    print("|------|-------------|--------------|------------|---------------|")
    for i, agency in enumerate(data["innerAgencies"]):
        print(f"| {i+1} | {agency['name']} | {agency['parentAgency']} | {agency['wordCount']:,} | {agency['sectionCount']:,} |")

def main():
    """Main function to run the scraper"""
    print("Starting CFR metrics scraper for all inner agencies...")
    data = get_all_agencies_with_inner()
    
    if data:
        # Save to a JSON file
        with open('cfr_metrics_all_data.json', 'w') as f:
            json.dump(data, f, indent=2)
        print("Data saved to cfr_metrics_all_data.json")
        
        # Print markdown tables
        print_markdown_tables(data)
    else:
        print("Failed to collect data")

if __name__ == "__main__":
    main() 