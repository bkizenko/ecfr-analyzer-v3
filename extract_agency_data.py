#!/usr/bin/env python3
import requests
import json
import re
import time
from collections import defaultdict

# Local UI server URL
LOCAL_UI_URL = "http://localhost:3001"

# Key agencies to scan (add more as needed)
TARGET_AGENCIES = [
    "agriculture-department",
    "treasury-department",
    "commerce-department",
    "defense-department",
    "education-department", 
    "energy-department",
    "health-and-human-services-department",
    "homeland-security-department",
    "housing-and-urban-development-department",
    "interior-department",
    "justice-department",
    "labor-department",
    "state-department",
    "transportation-department",
    "veterans-affairs-department",
    "environmental-protection-agency",
    "federal-communications-commission",
    "federal-reserve-system",
    "federal-trade-commission",
    "securities-and-exchange-commission"
]

def get_agency_page(agency_slug):
    """Get the HTML content of an agency page"""
    url = f"{LOCAL_UI_URL}/agency/{agency_slug}"
    print(f"Fetching agency page: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_inner_agencies_data(html_content, parent_agency_slug):
    """Extract inner agencies data from the HTML content"""
    if not html_content:
        return []
    
    print(f"Extracting inner agencies data for {parent_agency_slug}")
    
    # Extract the agency name from HTML
    agency_name_match = re.search(r'<title>(.*?) - CFR Metrics</title>', html_content)
    parent_agency_name = agency_name_match.group(1) if agency_name_match else format_agency_name(parent_agency_slug)
    
    # Extract the JavaScript object with the agencyMetrics data
    # This looks for:  "agencyMetrics":[{...}],"isSubAgency":true
    agency_metrics_match = re.search(r'"agencyMetrics":(\[.*?\]),"isSubAgency":true', html_content, re.DOTALL)
    
    if not agency_metrics_match:
        print(f"No inner agencies data found for {parent_agency_slug}")
        return []
    
    try:
        # Parse the JSON data
        json_data = agency_metrics_match.group(1)
        metrics = json.loads(json_data)
        
        # Format the inner agencies data
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
        
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON data for {parent_agency_slug}: {e}")
        print(f"JSON data: {json_data[:100]}...")  # Print the first 100 chars for debugging
        return []
    except Exception as e:
        print(f"Error processing inner agencies for {parent_agency_slug}: {e}")
        return []

def format_agency_name(agency_slug):
    """Format an agency slug into a readable name"""
    # Convert slug to a more readable name
    agency_name = ' '.join(word.capitalize() for word in agency_slug.split('-'))
    
    # Special case for department names
    if agency_name.endswith('Department'):
        agency_name = f"Department of {agency_name.replace(' Department', '')}"
    
    return agency_name

def generate_report(all_inner_agencies):
    """Generate a report of inner agencies data"""
    if not all_inner_agencies:
        print("No inner agencies data to report")
        return
    
    # Calculate total metrics
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
    print(f"Total Parent Agencies with Inner Agencies: {len(agencies_by_parent)}")
    print(f"Total Inner Agencies: {total_inner_agencies}")
    print(f"Total Word Count: {total_word_count:,}")
    print(f"Total Section Count: {total_section_count:,}\n")
    
    # Top 10 parent agencies by word count
    print("Top 10 Parent Agencies by Word Count:")
    for i, (parent, totals) in enumerate(sorted_parents[:10]):
        print(f"{i+1}. {parent}: {totals['totalWordCount']:,} words, {totals['innerAgencyCount']} inner agencies")
    
    # Generate Markdown report
    print("\nGenerating markdown report...")
    
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
    with open('inner_agencies_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("Markdown report saved to inner_agencies_report.md")
    
    # Save the raw data
    with open('inner_agencies_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_inner_agencies, f, indent=2)
    
    print("Inner agencies data saved to inner_agencies_data.json")
    
    # Create CSV version for easy import into spreadsheets
    with open('inner_agencies_data.csv', 'w', encoding='utf-8') as f:
        f.write("Inner Agency,Parent Agency,Word Count,Section Count\n")
        for agency in all_inner_agencies_sorted:
            f.write(f"\"{agency['name']}\",\"{agency['parentAgency']}\",{agency['wordCount']},{agency['sectionCount']}\n")
    
    print("CSV version saved to inner_agencies_data.csv")

def main():
    """Main function to extract inner agencies data for target agencies"""
    print(f"Starting extraction of inner agencies data for {len(TARGET_AGENCIES)} target agencies...")
    print(f"Using local UI server at {LOCAL_UI_URL}")
    
    all_inner_agencies = []
    
    # Process each target agency
    for i, agency_slug in enumerate(TARGET_AGENCIES):
        print(f"\nProcessing agency {i+1}/{len(TARGET_AGENCIES)}: {agency_slug}")
        
        # Get the agency page
        html_content = get_agency_page(agency_slug)
        
        if html_content:
            # Extract inner agencies data
            inner_agencies = extract_inner_agencies_data(html_content, agency_slug)
            
            # Add to the global list
            all_inner_agencies.extend(inner_agencies)
            
            # Short delay between requests to be nice to the local server
            if i < len(TARGET_AGENCIES) - 1:
                time.sleep(0.5)
    
    # Generate report
    if all_inner_agencies:
        generate_report(all_inner_agencies)
        print(f"Successfully processed {len(TARGET_AGENCIES)} agencies with {len(all_inner_agencies)} inner agencies")
    else:
        print("No inner agencies data found!")

if __name__ == "__main__":
    main() 