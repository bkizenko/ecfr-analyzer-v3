#!/usr/bin/env python3
import os
import re
import json
import requests
import time
import random
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agency_scraping.log'),
        logging.StreamHandler()
    ]
)

# Browser headers to mimic a real browser
BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://cfr-metrics.com/',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0'
}

# Concurrency settings
MAX_WORKERS = 4
RETRY_ATTEMPTS = 3
RETRY_DELAY = 5

def random_delay(min_sec=1.0, max_sec=3.0):
    """Add a small random delay between requests to avoid being rate-limited"""
    delay = random.uniform(min_sec, max_sec)
    logging.debug(f"Waiting {delay:.2f} seconds...")
    time.sleep(delay)

def get_all_agency_slugs():
    """Extract all agency slugs from the main page"""
    logging.info("Fetching the list of all agencies from the main page...")
    url = "https://cfr-metrics.com/"
    
    try:
        response = requests.get(url, headers=BROWSER_HEADERS)
        response.raise_for_status()
        
        # Extract agency links using regex
        # Looking for patterns like: href="/agency/agriculture-department"
        agency_links = re.findall(r'href="/agency/([^"]+)"', response.text)
        
        # Remove duplicates and sort
        unique_slugs = sorted(list(set(agency_links)))
        
        logging.info(f"Found {len(unique_slugs)} unique agency slugs")
        return unique_slugs
    
    except Exception as e:
        logging.error(f"Error fetching agency slugs: {e}")
        return []

def download_agency_html(agency_slug):
    """Download the HTML for a specific agency page with retries"""
    url = f"https://cfr-metrics.com/agency/{agency_slug}"
    
    for attempt in range(RETRY_ATTEMPTS):
        try:
            logging.info(f"Downloading HTML from {url} (attempt {attempt+1}/{RETRY_ATTEMPTS})")
            response = requests.get(url, headers=BROWSER_HEADERS)
            response.raise_for_status()
            
            # Ensure the agencies_html directory exists
            os.makedirs('agencies_html', exist_ok=True)
            
            # Save HTML to file
            html_path = f"agencies_html/agency_{agency_slug}.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            logging.info(f"Saved HTML to {html_path}")
            return html_path
        except requests.exceptions.RequestException as e:
            logging.warning(f"Request error for {agency_slug} (attempt {attempt+1}): {e}")
            if attempt < RETRY_ATTEMPTS - 1:
                sleep_time = RETRY_DELAY * (attempt + 1)
                logging.info(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                logging.error(f"Failed to download HTML for {agency_slug} after {RETRY_ATTEMPTS} attempts")
                return None
        except Exception as e:
            logging.error(f"Unexpected error downloading HTML for {agency_slug}: {e}")
            return None

def extract_inner_agencies_from_html(html_path, agency_slug):
    """Extract inner agencies data from the HTML file"""
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Extract the JavaScript object with the agencyMetrics data
        # This looks for:  "agencyMetrics":[{...}],"isSubAgency":true
        agency_metrics_match = re.search(r'"agencyMetrics":(\[.*?\]),"isSubAgency":true', html_content, re.DOTALL)
        
        if not agency_metrics_match:
            logging.info(f"No inner agencies found for {agency_slug} in the HTML")
            return []
        
        # Parse the JSON data
        json_data = agency_metrics_match.group(1)
        metrics = json.loads(json_data)
        
        # Extract agency name for better reporting
        agency_name_match = re.search(r'"agency":\{"name":"([^"]+)"', html_content)
        agency_name = agency_name_match.group(1) if agency_name_match else format_agency_name(agency_slug)
        
        # Format the inner agencies data
        inner_agencies = format_inner_agencies_data(metrics, agency_slug, agency_name)
        
        return inner_agencies
    except json.JSONDecodeError as e:
        logging.error(f"JSON parse error for {agency_slug}: {e}")
        return []
    except Exception as e:
        logging.error(f"Error extracting metrics from {html_path}: {e}")
        return []

def format_agency_name(agency_slug):
    """Format an agency slug into a readable name"""
    # Convert slug to a more readable name
    agency_name = ' '.join(word.capitalize() for word in agency_slug.split('-'))
    
    # Special case for department names
    if agency_name.endswith('Department'):
        agency_name = f"Department of {agency_name.replace(' Department', '')}"
    
    return agency_name

def format_inner_agencies_data(metrics, parent_agency_slug, parent_agency_name=None):
    """Format the inner agencies data for easier readability"""
    if parent_agency_name is None:
        parent_agency_name = format_agency_name(parent_agency_slug)
    
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
    
    if inner_agencies:
        logging.info(f"Found {len(inner_agencies)} inner agencies for {parent_agency_name}")
    
    return inner_agencies

def process_agency(agency_slug):
    """Process an individual agency to extract inner agencies data"""
    logging.info(f"Processing agency: {agency_slug}")
    
    html_path = None
    # Check if we already have the HTML file
    expected_path = f"agencies_html/agency_{agency_slug}.html"
    if os.path.exists(expected_path):
        logging.info(f"Using existing HTML file: {expected_path}")
        html_path = expected_path
    else:
        # Download the HTML
        html_path = download_agency_html(agency_slug)
    
    if not html_path:
        logging.error(f"Failed to get HTML for {agency_slug}")
        return []
    
    # Extract inner agencies from the HTML
    inner_agencies = extract_inner_agencies_from_html(html_path, agency_slug)
    
    if inner_agencies:
        # Save individual agency data
        os.makedirs('agency_data', exist_ok=True)
        save_path = f"agency_data/{agency_slug}_inner_agencies.json"
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(inner_agencies, f, indent=2)
        
        logging.info(f"Saved inner agencies data for {agency_slug} to {save_path}")
    else:
        logging.info(f"No inner agencies found for {agency_slug}")
    
    return inner_agencies

def generate_stats_and_report(all_inner_agencies):
    """Generate statistics and a report based on the inner agencies data"""
    if not all_inner_agencies:
        logging.warning("No inner agencies data to generate report")
        return
    
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
    
    # Log summary
    logging.info("\n=== INNER AGENCIES STATISTICS ===")
    logging.info(f"Total Parent Agencies with Inner Agencies: {len(agencies_by_parent)}")
    logging.info(f"Total Inner Agencies: {total_inner_agencies}")
    logging.info(f"Total Word Count: {total_word_count:,}")
    logging.info(f"Total Section Count: {total_section_count:,}\n")
    
    # Top 10 parent agencies by word count
    logging.info("Top 10 Parent Agencies by Word Count:")
    for i, (parent, totals) in enumerate(sorted_parents[:10]):
        logging.info(f"{i+1}. {parent}: {totals['totalWordCount']:,} words, {totals['innerAgencyCount']} inner agencies")
    
    # Generate Markdown report
    logging.info("\nGenerating markdown report...")
    
    report = "# Inner Agencies Word Count Analysis\n\n"
    
    report += "## Overview Statistics\n\n"
    report += f"- **Total Parent Agencies with Inner Agencies:** {len(agencies_by_parent)}\n"
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
    report += "| Rank | Parent Agency | Total Word Count | Inner Agency Count | Section Count |\n"
    report += "|------|---------------|------------------|--------------------|--------------|\n"
    
    for i, (parent, totals) in enumerate(sorted_parents):
        report += f"| {i+1} | {parent} | {totals['totalWordCount']:,} | {totals['innerAgencyCount']} | {totals['totalSectionCount']:,} |\n"
    
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
    with open('all_inner_agencies_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    logging.info("Markdown report saved to all_inner_agencies_report.md")
    
    # Save the raw data
    with open('all_inner_agencies.json', 'w', encoding='utf-8') as f:
        json.dump(all_inner_agencies, f, indent=2)
    
    logging.info("All inner agencies data saved to all_inner_agencies.json")
    
    # Create CSV version for easy import into spreadsheets
    with open('all_inner_agencies.csv', 'w', encoding='utf-8') as f:
        f.write("Inner Agency,Parent Agency,Word Count,Section Count\n")
        for agency in all_inner_agencies_sorted:
            f.write(f"\"{agency['name']}\",\"{agency['parentAgency']}\",{agency['wordCount']},{agency['sectionCount']}\n")
    
    logging.info("CSV version saved to all_inner_agencies.csv")

def main():
    """Main function to extract and process inner agencies data for all agencies"""
    logging.info("Starting extraction of inner agencies data for all agencies...")
    
    # Create directories if they don't exist
    os.makedirs('agencies_html', exist_ok=True)
    os.makedirs('agency_data', exist_ok=True)
    
    # Get all agency slugs
    agency_slugs = get_all_agency_slugs()
    
    if not agency_slugs:
        logging.error("Failed to get agency slugs. Exiting.")
        return
    
    # Save the list of agencies
    with open('all_agency_slugs.json', 'w', encoding='utf-8') as f:
        json.dump(agency_slugs, f, indent=2)
    
    all_inner_agencies = []
    
    # Process agencies with thread pool for controlled concurrency
    logging.info(f"Processing {len(agency_slugs)} agencies with {MAX_WORKERS} workers...")
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all tasks and create a mapping of futures to agency slugs
        future_to_agency = {executor.submit(process_agency, slug): slug for slug in agency_slugs}
        
        # Process results as they complete
        for future in as_completed(future_to_agency):
            agency_slug = future_to_agency[future]
            try:
                inner_agencies = future.result()
                all_inner_agencies.extend(inner_agencies)
                # Random delay between completing tasks
                random_delay(1.0, 2.0)
            except Exception as e:
                logging.error(f"Error processing {agency_slug}: {e}")
    
    # Generate stats and report
    if all_inner_agencies:
        generate_stats_and_report(all_inner_agencies)
        logging.info(f"Successfully processed {len(agency_slugs)} agencies with {len(all_inner_agencies)} inner agencies")
    else:
        logging.warning("No inner agencies data found!")

if __name__ == "__main__":
    main()
