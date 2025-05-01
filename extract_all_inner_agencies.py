#!/usr/bin/env python3
import requests
import json
import re
import time
import random
from collections import defaultdict

# Browser headers to mimic a real browser
BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://cfr-metrics.com/',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0'
}

def random_delay(min_sec=1.0, max_sec=2.5):
    """Add a small random delay between requests to avoid being rate-limited"""
    delay = random.uniform(min_sec, max_sec)
    print(f"Waiting {delay:.2f} seconds...")
    time.sleep(delay)

def extract_agency_data_from_json(html_content):
    """Extract the agency data directly from the embedded JSON in the HTML page"""
    # Look for the Next.js data script
    script_pattern = r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>'
    script_match = re.search(script_pattern, html_content)
    
    if not script_match:
        print("Could not find Next.js data script")
        return None
        
    # Extract and parse the JSON data
    try:
        json_data = json.loads(script_match.group(1))
        
        # Navigate to the agency data
        if 'props' in json_data and 'pageProps' in json_data['props'] and 'props' in json_data['props']['pageProps']:
            page_props = json_data['props']['pageProps']['props']
            
            if 'agency' in page_props:
                agency = page_props['agency']
                
                # Extract agency info
                agency_data = {
                    "name": agency.get('name', 'Unknown'),
                    "slug": agency.get('slug', 'unknown'),
                    "wordCount": agency.get('metrics', {}).get('wordCount', 0),
                    "sectionCount": agency.get('metrics', {}).get('sectionCount', 0),
                    "innerAgencies": []
                }
                
                # Extract inner agencies data
                for child in agency.get('children', []):
                    if child is None:
                        continue
                    
                    inner_agency = {
                        "name": child.get('name', 'Unknown'),
                        "slug": child.get('slug', 'unknown'),
                        "wordCount": child.get('metrics', {}).get('wordCount', 0) if 'metrics' in child else 0,
                        "sectionCount": child.get('metrics', {}).get('sectionCount', 0) if 'metrics' in child else 0
                    }
                    agency_data["innerAgencies"].append(inner_agency)
                
                return agency_data
    
    except Exception as e:
        print(f"Error parsing JSON: {e}")
    
    return None

def get_agency_data(agency_slug):
    """Get data for a specific agency by its slug"""
    url = f"https://cfr-metrics.com/agency/{agency_slug}"
    print(f"Fetching data from {url}")
    
    try:
        response = requests.get(url, headers=BROWSER_HEADERS)
        if response.status_code != 200:
            print(f"Failed to get data for {agency_slug}: HTTP {response.status_code}")
            return None
            
        # Extract agency data from the HTML
        return extract_agency_data_from_json(response.text)
    
    except Exception as e:
        print(f"Error fetching {agency_slug}: {e}")
        return None

def get_all_agencies_with_inner():
    """Get all agencies data first, then fetch inner agency data for each"""
    # Known parent agencies from our previous data
    parent_agencies = [
        {"slug": "agriculture-department", "name": "Department of Agriculture"},
        {"slug": "commerce-department", "name": "Department of Commerce"},
        {"slug": "defense-department", "name": "Department of Defense"},
        {"slug": "education-department", "name": "Department of Education"},
        {"slug": "energy-department", "name": "Department of Energy"},
        {"slug": "health-and-human-services-department", "name": "Department of Health and Human Services"},
        {"slug": "homeland-security-department", "name": "Department of Homeland Security"},
        {"slug": "housing-and-urban-development-department", "name": "Department of Housing and Urban Development"},
        {"slug": "interior-department", "name": "Department of Interior"},
        {"slug": "justice-department", "name": "Department of Justice"},
        {"slug": "labor-department", "name": "Department of Labor"},
        {"slug": "transportation-department", "name": "Department of Transportation"},
        {"slug": "treasury-department", "name": "Department of Treasury"},
        {"slug": "veterans-affairs-department", "name": "Department of Veterans Affairs"},
        {"slug": "executive-office-of-the-president", "name": "Executive Office of the President"},
        {"slug": "federal-labor-relations-authority", "name": "Federal Labor Relations Authority"},
        {"slug": "federal-reserve-system", "name": "Federal Reserve System"},
        {"slug": "general-services-administration", "name": "General Services Administration"},
        {"slug": "library-of-congress", "name": "Library of Congress"},
        {"slug": "management-and-budget-office", "name": "Office of Management and Budget"},
        {"slug": "national-archives-and-records-administration", "name": "National Archives and Records Administration"},
        {"slug": "national-foundation-on-the-arts-and-the-humanities", "name": "National Foundation on the Arts and the Humanities"}
    ]
    
    # Process all parent agencies
    all_agencies = []
    all_inner_agencies = []
    
    for i, agency in enumerate(parent_agencies):
        print(f"Processing {i+1}/{len(parent_agencies)}: {agency['name']} ({agency['slug']})")
        
        agency_data = get_agency_data(agency['slug'])
        if agency_data:
            all_agencies.append(agency_data)
            
            # Add inner agencies to a flat list
            for inner in agency_data["innerAgencies"]:
                inner_with_parent = inner.copy()
                inner_with_parent["parentAgency"] = agency_data["name"]
                all_inner_agencies.append(inner_with_parent)
            
            # Save progress after each successful agency
            with open(f'agency_{agency["slug"]}.json', 'w') as f:
                json.dump(agency_data, f, indent=2)
        
        # Add delay to avoid rate limiting
        random_delay()
    
    # Sort agencies and inner agencies by word count
    all_agencies.sort(key=lambda x: x["wordCount"], reverse=True)
    all_inner_agencies.sort(key=lambda x: x["wordCount"], reverse=True)
    
    return {
        "agencies": all_agencies,
        "innerAgencies": all_inner_agencies
    }

def print_markdown_tables(data):
    """Print the metrics in markdown format tables"""
    # Calculate total metrics
    total_agencies = len(data["agencies"])
    total_inner_agencies = len(data["innerAgencies"])
    total_words = sum(agency["wordCount"] for agency in data["agencies"])
    total_sections = sum(agency["sectionCount"] for agency in data["agencies"])
    total_inner_words = sum(inner["wordCount"] for inner in data["innerAgencies"])
    total_inner_sections = sum(inner["sectionCount"] for inner in data["innerAgencies"])
    
    print("\n# CFR Metrics Summary")
    
    print(f"\n## Overall Totals")
    print(f"- Total Agencies: {total_agencies}")
    print(f"- Total Words (Agencies): {total_words:,}")
    print(f"- Total Sections (Agencies): {total_sections:,}")
    print(f"- Total Inner Agencies: {total_inner_agencies}")
    print(f"- Total Words (Inner Agencies): {total_inner_words:,}")
    print(f"- Total Sections (Inner Agencies): {total_inner_sections:,}")
    
    print("\n## Top Agencies by Word Count")
    print("| Rank | Agency | Word Count | Section Count | Inner Agencies |")
    print("|------|--------|------------|---------------|----------------|")
    for i, agency in enumerate(data["agencies"][:30]):
        print(f"| {i+1} | {agency['name']} | {agency['wordCount']:,} | {agency['sectionCount']:,} | {len(agency['innerAgencies'])} |")
    
    print("\n## All Inner Agencies by Word Count")
    print("| Rank | Inner Agency | Parent Agency | Word Count | Section Count |")
    print("|------|-------------|--------------|------------|---------------|")
    for i, agency in enumerate(data["innerAgencies"]):
        print(f"| {i+1} | {agency['name']} | {agency['parentAgency']} | {agency['wordCount']:,} | {agency['sectionCount']:,} |")
    
    # Agency-wise inner agencies
    print("\n## Inner Agencies by Parent Agency")
    for agency in data["agencies"]:
        if len(agency["innerAgencies"]) > 0:
            print(f"\n### {agency['name']}")
            print("| Inner Agency | Word Count | Section Count |")
            print("|-------------|------------|---------------|")
            sorted_inner = sorted(agency["innerAgencies"], key=lambda x: x["wordCount"], reverse=True)
            for inner in sorted_inner:
                print(f"| {inner['name']} | {inner['wordCount']:,} | {inner['sectionCount']:,} |")

def main():
    """Main function to execute the script"""
    print("Starting to extract inner agency data for all agencies...")
    data = get_all_agencies_with_inner()
    
    if data:
        # Save to a combined JSON file
        with open('all_agencies_and_inner.json', 'w') as f:
            json.dump(data, f, indent=2)
        print("Data saved to all_agencies_and_inner.json")
        
        # Print statistics in markdown format
        print_markdown_tables(data)
    else:
        print("Failed to collect data")

if __name__ == "__main__":
    main() 