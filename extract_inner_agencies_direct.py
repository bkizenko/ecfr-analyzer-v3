#!/usr/bin/env python3
import os
import re
import json
import requests
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

# Main agency slugs to scrape
MAIN_AGENCIES = [
    'agriculture-department',
    'commerce-department',
    'defense-department',
    'education-department',
    'energy-department',
    'health-and-human-services-department',
    'homeland-security-department',
    'housing-and-urban-development-department',
    'interior-department',
    'justice-department',
    'labor-department',
    'state-department',
    'transportation-department',
    'treasury-department',
    'veterans-affairs-department'
]

def random_delay(min_sec=1.0, max_sec=2.5):
    """Add a small random delay between requests to avoid being rate-limited"""
    delay = random.uniform(min_sec, max_sec)
    print(f"Waiting {delay:.2f} seconds...")
    time.sleep(delay)

def download_agency_html(agency_slug):
    """Download the HTML for a specific agency page"""
    url = f"https://cfr-metrics.com/agency/{agency_slug}"
    print(f"Downloading HTML from {url}")
    
    try:
        response = requests.get(url, headers=BROWSER_HEADERS)
        response.raise_for_status()
        
        # Ensure the agencies_html directory exists
        os.makedirs('agencies_html', exist_ok=True)
        
        # Save HTML to file
        html_path = f"agencies_html/agency_{agency_slug}.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"Saved HTML to {html_path}")
        return html_path
    except Exception as e:
        print(f"Error downloading HTML for {agency_slug}: {e}")
        return None

def extract_agency_metrics_from_html(html_path, agency_slug):
    """Extract agency metrics from the HTML file"""
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Extract the JavaScript object with the agencyMetrics data
        # This looks for:  "agencyMetrics":[{...}],"isSubAgency":true
        agency_metrics_match = re.search(r'"agencyMetrics":(\[.*?\]),"isSubAgency":true', html_content, re.DOTALL)
        
        if not agency_metrics_match:
            print(f"Could not find agency metrics for {agency_slug} in the HTML")
            return None
        
        # Parse the JSON data
        json_data = agency_metrics_match.group(1)
        metrics = json.loads(json_data)
        
        return metrics
    except Exception as e:
        print(f"Error extracting metrics from {html_path}: {e}")
        return None

def format_inner_agencies_data(metrics, parent_agency_slug):
    """Format the inner agencies data for easier readability"""
    # Convert slug to a more readable name
    parent_agency_name = ' '.join(word.capitalize() for word in parent_agency_slug.split('-'))
    
    # Special case for department names
    if parent_agency_name.endswith('Department'):
        parent_agency_name = f"Department of {parent_agency_name.replace(' Department', '')}"
    
    inner_agencies = []
    
    for item in metrics:
        agency_info = item.get('agency', {})
        metrics_data = item.get('metrics', {})
        
        inner_agencies.append({
            'name': agency_info.get('name', 'Unknown'),
            'slug': agency_info.get('slug', ''),
            'cfr_references': agency_info.get('cfr_references', []),
            'wordCount': metrics_data.get('wordCount', 0),
            'sectionCount': metrics_data.get('sectionCount', 0),
            'parentAgency': parent_agency_name,
            'parentAgencySlug': parent_agency_slug
        })
    
    # Sort by word count
    inner_agencies.sort(key=lambda x: x['wordCount'], reverse=True)
    
    print(f"Found {len(inner_agencies)} inner agencies for {parent_agency_name}")
    return inner_agencies

def process_agency(agency_slug, all_inner_agencies):
    """Process an individual agency to extract inner agencies data"""
    print(f"Processing agency: {agency_slug}")
    
    html_path = None
    # Check if we already have the HTML file
    expected_path = f"agencies_html/agency_{agency_slug}.html"
    if os.path.exists(expected_path):
        print(f"Using existing HTML file: {expected_path}")
        html_path = expected_path
    else:
        # Download the HTML
        html_path = download_agency_html(agency_slug)
        if html_path:
            random_delay()  # Add delay after download
    
    if not html_path:
        print(f"Failed to get HTML for {agency_slug}")
        return
    
    # Extract metrics from the HTML
    metrics = extract_agency_metrics_from_html(html_path, agency_slug)
    
    if not metrics:
        print(f"No metrics found for {agency_slug}")
        return
    
    # Format the inner agencies data
    inner_agencies = format_inner_agencies_data(metrics, agency_slug)
    
    # Add to the global list
    all_inner_agencies.extend(inner_agencies)
    
    # Save individual agency data
    os.makedirs('agency_data', exist_ok=True)
    with open(f"agency_data/{agency_slug}_inner_agencies.json", 'w', encoding='utf-8') as f:
        json.dump(inner_agencies, f, indent=2)
    
    print(f"Saved inner agencies data for {agency_slug}")

def generate_stats_and_report(all_inner_agencies):
    """Generate statistics and a report based on the inner agencies data"""
    # Get total metrics
    total_inner_agencies = len(all_inner_agencies)
    total_word_count = sum(agency['wordCount'] for agency in all_inner_agencies)
    total_section_count = sum(agency['sectionCount'] for agency in all_inner_agencies)
    
    # Group by parent agency
    agencies_by_parent = defaultdict(list)
    for agency in all_inner_agencies:
        agencies_by_parent[agency['parentAgency']].append(agency)
    
    # Calculate parent agency totals
    parent_totals = {}
    for parent, children in agencies_by_parent.items():
        parent_totals[parent] = {
            'innerAgencyCount': len(children),
            'totalWordCount': sum(child['wordCount'] for child in children),
            'totalSectionCount': sum(child['sectionCount'] for child in children)
        }
    
    # Sort parent agencies by word count
    sorted_parents = sorted(parent_totals.items(), key=lambda x: x[1]['totalWordCount'], reverse=True)
    
    # Print summary
    print("\n=== INNER AGENCIES STATISTICS ===")
    print(f"Total Inner Agencies: {total_inner_agencies}")
    print(f"Total Word Count: {total_word_count:,}")
    print(f"Total Section Count: {total_section_count:,}\n")
    
    print("Parent Agency Word Counts (sorted by total words in inner agencies):")
    for parent, totals in sorted_parents:
        print(f"{parent}: {totals['totalWordCount']:,} words, {totals['innerAgencyCount']} inner agencies")
    
    # Generate Markdown report
    print("\nGenerating markdown report...")
    
    report = "# Inner Agencies Word Count Analysis\n\n"
    
    report += "## Overview Statistics\n\n"
    report += f"- **Total Inner Agencies:** {total_inner_agencies}\n"
    report += f"- **Total Inner Agencies Word Count:** {total_word_count:,}\n"
    report += f"- **Total Inner Agencies Section Count:** {total_section_count:,}\n\n"
    
    report += "## Top 30 Inner Agencies by Word Count\n\n"
    report += "| Rank | Inner Agency | Parent Agency | Word Count | Section Count |\n"
    report += "|------|-------------|---------------|------------|---------------|\n"
    
    # Sort all inner agencies by word count
    all_inner_agencies_sorted = sorted(all_inner_agencies, key=lambda x: x['wordCount'], reverse=True)
    
    for i, agency in enumerate(all_inner_agencies_sorted[:30]):
        report += f"| {i+1} | {agency['name']} | {agency['parentAgency']} | {agency['wordCount']:,} | {agency['sectionCount']:,} |\n"
    
    report += "\n## Parent Agencies Ranked by Inner Agency Word Count\n\n"
    report += "| Rank | Parent Agency | Total Word Count | Inner Agency Count |\n"
    report += "|------|---------------|------------------|--------------------|\n"
    
    for i, (parent, totals) in enumerate(sorted_parents):
        report += f"| {i+1} | {parent} | {totals['totalWordCount']:,} | {totals['innerAgencyCount']} |\n"
    
    report += "\n## Inner Agencies by Parent Agency\n\n"
    
    for parent, totals in sorted_parents:
        children = agencies_by_parent[parent]
        children.sort(key=lambda x: x['wordCount'], reverse=True)
        
        report += f"### {parent} ({totals['innerAgencyCount']} inner agencies, {totals['totalWordCount']:,} words)\n\n"
        report += "| Inner Agency | Word Count | Section Count |\n"
        report += "|-------------|------------|---------------|\n"
        
        for child in children:
            report += f"| {child['name']} | {child['wordCount']:,} | {child['sectionCount']:,} |\n"
        
        report += "\n"
    
    # Save report
    with open('inner_agencies_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("Markdown report saved to inner_agencies_report.md")
    
    # Save the raw data
    with open('all_inner_agencies.json', 'w', encoding='utf-8') as f:
        json.dump(all_inner_agencies, f, indent=2)
    
    print("All inner agencies data saved to all_inner_agencies.json")

def main():
    """Main function to extract and process inner agencies data"""
    print("Starting extraction of inner agencies data...")
    
    # Create directories if they don't exist
    os.makedirs('agencies_html', exist_ok=True)
    os.makedirs('agency_data', exist_ok=True)
    
    all_inner_agencies = []
    
    # Process each agency
    for i, agency_slug in enumerate(MAIN_AGENCIES):
        print(f"\nProcessing agency {i+1}/{len(MAIN_AGENCIES)}: {agency_slug}")
        process_agency(agency_slug, all_inner_agencies)
        
        if i < len(MAIN_AGENCIES) - 1:
            random_delay(2.0, 4.0)  # Add longer delay between agencies
    
    # Generate stats and report
    if all_inner_agencies:
        generate_stats_and_report(all_inner_agencies)
    else:
        print("No inner agencies data found!")

if __name__ == "__main__":
    main() 