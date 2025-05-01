#!/usr/bin/env python3
import re
import json

def extract_agency_metrics():
    """Extract agency metrics data from the HTML file using regex for the agencyMetrics array"""
    
    with open('agency_treasury-department.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Find the agencyMetrics JSON data in the file
    pattern = r'\"agencyMetrics\":\[(.*?)\],\"isSubAgency\"'
    match = re.search(pattern, html_content, re.DOTALL)
    
    if not match:
        print("Could not find agencyMetrics data in the HTML file")
        return None
    
    # Create proper JSON data
    json_data = match.group(1)
    agencies_json = "[" + json_data + "]"
    
    try:
        # Parse the JSON data
        agencies = json.loads(agencies_json)
        
        # Format the data for easier readability
        formatted_agencies = []
        for agency in agencies:
            agency_info = agency['agency']
            metrics = agency['metrics']
            
            formatted_agencies.append({
                'name': agency_info.get('name', 'Unknown'),
                'wordCount': metrics.get('wordCount', 0),
                'sectionCount': metrics.get('sectionCount', 0),
            })
        
        # Sort by word count (descending)
        formatted_agencies.sort(key=lambda x: x['wordCount'], reverse=True)
        
        return formatted_agencies
    
    except Exception as e:
        print(f"Error parsing agency metrics data: {e}")
        return None

def main():
    """Extract and display Treasury inner agencies data"""
    print("Extracting Treasury inner agencies data...")
    
    agencies = extract_agency_metrics()
    
    if agencies:
        # Print a Markdown table of the results
        print("\n## Department of Treasury Inner Agencies by Word Count")
        print("| Rank | Inner Agency | Word Count | Section Count |")
        print("|------|-------------|------------|---------------|")
        for i, agency in enumerate(agencies):
            print(f"| {i+1} | {agency['name']} | {agency['wordCount']:,} | {agency['sectionCount']:,} |")
        
        # Save to JSON file
        with open('treasury_inner_agencies.json', 'w') as f:
            json.dump(agencies, f, indent=2)
        
        print("\nData saved to treasury_inner_agencies.json")
    else:
        print("Failed to extract inner agencies data")

if __name__ == "__main__":
    main() 