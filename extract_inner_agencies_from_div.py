#!/usr/bin/env python3
import os
import re
import json
from collections import defaultdict
from bs4 import BeautifulSoup

def extract_inner_agencies_from_html(html_file, parent_agency_name):
    """Extract inner agencies data from HTML by finding the agencyMetrics property in the JavaScript"""
    print(f"Processing {html_file} for {parent_agency_name}...")
    
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Look for the agencyMetrics JavaScript object in the HTML
        # The data is in a property of a React component
        pattern = r'"agencyMetrics":\[(.*?)\],"isSubAgency":true'
        match = re.search(pattern, html_content, re.DOTALL)
        
        if not match:
            print(f"Could not find agencyMetrics for {parent_agency_name} in the HTML")
            return []
        
        try:
            # Extract the JSON data and wrap it in square brackets to make it a valid JSON array
            json_data = "[" + match.group(1) + "]"
            
            # Parse the JSON data
            metrics = json.loads(json_data)
            
            # Format the data for easier readability
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
                    'parentAgency': parent_agency_name
                })
            
            # Sort by word count
            inner_agencies.sort(key=lambda x: x['wordCount'], reverse=True)
            print(f"Found {len(inner_agencies)} inner agencies for {parent_agency_name}")
            return inner_agencies
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON data for {parent_agency_name}: {e}")
            return []
        
    except Exception as e:
        print(f"Error processing {html_file}: {e}")
        return []

def process_agency_html_files():
    """Process all HTML files to extract inner agencies data"""
    all_inner_agencies = []
    html_dir = 'agencies_html'
    
    # Create output directory if it doesn't exist
    os.makedirs('parsed_inner_agencies', exist_ok=True)
    
    if not os.path.exists(html_dir):
        print(f"Directory {html_dir} not found")
        return []
    
    # Get all HTML files in the directory
    html_files = [f for f in os.listdir(html_dir) if f.startswith('agency_') and f.endswith('.html')]
    
    if not html_files:
        print(f"No HTML files found in {html_dir}")
        return []
    
    print(f"Found {len(html_files)} HTML files to process")
    
    # Process each HTML file
    for html_file in html_files:
        agency_slug = html_file.replace('agency_', '').replace('.html', '')
        
        # Convert slug to name - replace hyphens with spaces and capitalize
        parent_agency_name = ' '.join(word.capitalize() for word in agency_slug.split('-'))
        
        # Special case for department names
        if parent_agency_name.endswith('Department'):
            parent_agency_name = f"Department of {parent_agency_name.replace(' Department', '')}"
        
        # Extract inner agencies
        inner_agencies = extract_inner_agencies_from_html(os.path.join(html_dir, html_file), parent_agency_name)
        
        # Save to individual JSON file
        with open(f'parsed_inner_agencies/{agency_slug}.json', 'w') as f:
            json.dump(inner_agencies, f, indent=2)
        
        # Add to the global list
        all_inner_agencies.extend(inner_agencies)
    
    # Save all inner agencies to a single file
    with open('all_inner_agencies.json', 'w') as f:
        json.dump(all_inner_agencies, f, indent=2)
    
    # Generate statistics
    agencies_by_parent = defaultdict(list)
    for agency in all_inner_agencies:
        agencies_by_parent[agency['parentAgency']].append(agency)
    
    # Calculate statistics
    total_inner_agencies = len(all_inner_agencies)
    total_word_count = sum(agency['wordCount'] for agency in all_inner_agencies)
    total_section_count = sum(agency['sectionCount'] for agency in all_inner_agencies)
    
    # Print statistics
    print(f"\n=== INNER AGENCIES STATISTICS ===")
    print(f"Total Inner Agencies: {total_inner_agencies}")
    print(f"Total Word Count: {total_word_count:,}")
    print(f"Total Section Count: {total_section_count:,}")
    
    # Generate a markdown report
    generate_markdown_report(all_inner_agencies, agencies_by_parent)
    
    return all_inner_agencies

def generate_markdown_report(all_inner_agencies, agencies_by_parent):
    """Generate a markdown report of inner agencies data"""
    # Sort inner agencies by word count
    all_inner_agencies.sort(key=lambda x: x['wordCount'], reverse=True)
    
    # Calculate totals
    total_inner_agencies = len(all_inner_agencies)
    total_word_count = sum(agency['wordCount'] for agency in all_inner_agencies)
    total_section_count = sum(agency['sectionCount'] for agency in all_inner_agencies)
    
    # Create report
    report = "# Inner Agencies Word Count Analysis\n\n"
    
    report += "## Overview Statistics\n\n"
    report += f"- **Total Inner Agencies:** {total_inner_agencies}\n"
    report += f"- **Total Inner Agencies Word Count:** {total_word_count:,}\n"
    report += f"- **Total Inner Agencies Section Count:** {total_section_count:,}\n\n"
    
    report += "## Top 30 Inner Agencies by Word Count\n\n"
    report += "| Rank | Inner Agency | Parent Agency | Word Count | Section Count |\n"
    report += "|------|-------------|---------------|------------|---------------|\n"
    for i, agency in enumerate(all_inner_agencies[:30]):
        report += f"| {i+1} | {agency['name']} | {agency['parentAgency']} | {agency['wordCount']:,} | {agency['sectionCount']:,} |\n"
    
    # Group inner agencies by parent
    report += "\n## Inner Agencies Grouped by Parent Agency\n\n"
    
    # Sort parent agencies by total word count of inner agencies
    parent_word_counts = {}
    for parent, children in agencies_by_parent.items():
        parent_word_counts[parent] = sum(child['wordCount'] for child in children)
    
    sorted_parents = sorted(parent_word_counts.items(), key=lambda x: x[1], reverse=True)
    
    for parent_name, total_words in sorted_parents:
        children = agencies_by_parent[parent_name]
        children.sort(key=lambda x: x['wordCount'], reverse=True)
        
        report += f"### {parent_name} ({len(children)} inner agencies, {total_words:,} words)\n\n"
        report += "| Inner Agency | Word Count | Section Count |\n"
        report += "|-------------|------------|---------------|\n"
        for child in children:
            report += f"| {child['name']} | {child['wordCount']:,} | {child['sectionCount']:,} |\n"
        report += "\n"
    
    # Save to file
    with open('inner_agencies_report.md', 'w') as f:
        f.write(report)
    
    print("Markdown report saved to inner_agencies_report.md")

if __name__ == "__main__":
    process_agency_html_files() 