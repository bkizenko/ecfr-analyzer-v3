#!/usr/bin/env python3
import json
import re
from bs4 import BeautifulSoup

def extract_agency_data_from_html(html_file):
    """Extract agencies data from the HTML file"""
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Look for the inner agencies data in the script tag
    agency_data_match = re.search(r'"agencyMetrics":\[([^\]]*)\]', html_content)
    if not agency_data_match:
        print("Could not find agency metrics data in HTML")
        return None
    
    # Clean up the JSON and parse it
    try:
        json_str = "[" + agency_data_match.group(1) + "]"
        # Fix any potential issues with the JSON formatting
        json_str = json_str.replace('\\"', '"')
        json_str = re.sub(r'(\w+):', r'"\1":', json_str)
        json_str = re.sub(r'\'', r'"', json_str)
        
        inner_agencies_data = json.loads(json_str)
        
        # Format the data for display
        formatted_data = []
        for item in inner_agencies_data:
            agency_info = item.get("agency", {})
            metrics = item.get("metrics", {})
            
            formatted_data.append({
                "name": agency_info.get("name", "Unknown"),
                "slug": agency_info.get("slug", "unknown"),
                "wordCount": metrics.get("wordCount", 0),
                "sectionCount": metrics.get("sectionCount", 0)
            })
        
        return formatted_data
    
    except Exception as e:
        print(f"Error parsing inner agencies data: {e}")
        return None

def main():
    """Main function to process the Treasury HTML file"""
    print("Extracting inner agencies data from Department of Treasury HTML file...")
    
    inner_agencies = extract_agency_data_from_html("agency_treasury-department.html")
    
    if inner_agencies:
        # Sort by word count (descending)
        inner_agencies.sort(key=lambda x: x["wordCount"], reverse=True)
        
        # Print a markdown table of the inner agencies
        print("\n## Department of Treasury Inner Agencies by Word Count")
        print("| Rank | Inner Agency | Word Count | Section Count |")
        print("|------|-------------|------------|---------------|")
        for i, agency in enumerate(inner_agencies):
            print(f"| {i+1} | {agency['name']} | {agency['wordCount']:,} | {agency['sectionCount']:,} |")
        
        # Save to JSON
        with open('treasury_inner_agencies.json', 'w') as f:
            json.dump(inner_agencies, f, indent=2)
        print("\nData saved to treasury_inner_agencies.json")
    else:
        print("Failed to extract inner agencies data")

if __name__ == "__main__":
    main() 