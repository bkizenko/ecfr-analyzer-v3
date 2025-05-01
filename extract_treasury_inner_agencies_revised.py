#!/usr/bin/env python3
import json
import re

def extract_agency_metrics(html_file):
    """Extract agency metrics data from the HTML file"""
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Look for the agencyMetrics section in the script tag
    pattern = r'"agencyMetrics":\s*\[\s*(\{.+?\}\})\s*\]'
    metrics_match = re.search(pattern, html_content, re.DOTALL)
    
    if not metrics_match:
        print("Could not find agencyMetrics in the HTML file.")
        return None
    
    # Get the raw JSON string with the agency metrics
    metrics_text = metrics_match.group(0)
    
    # Create a valid JSON string by wrapping it in curly braces
    json_str = '{' + metrics_text + '}'
    
    try:
        # Normalize JSON (fix any issues with quotes, etc.)
        json_str = json_str.replace("\\", "\\\\")
        
        # Parse the JSON data
        data = json.loads(json_str)
        inner_agencies = []
        
        # Extract the inner agencies data
        for item in data["agencyMetrics"]:
            agency_info = item.get("agency", {})
            metrics = item.get("metrics", {})
            
            inner_agencies.append({
                "name": agency_info.get("name", "Unknown"),
                "slug": agency_info.get("slug", "unknown"),
                "wordCount": metrics.get("wordCount", 0),
                "sectionCount": metrics.get("sectionCount", 0)
            })
        
        return inner_agencies
    
    except Exception as e:
        print(f"Error parsing inner agencies data: {e}")
        # Try a more manual approach using regex
        try:
            # Extract each agency metric individually
            agency_pattern = r'{"agency":{[^}]+},"metrics":{[^}]+}}'
            agencies_data = re.findall(agency_pattern, metrics_text, re.DOTALL)
            
            inner_agencies = []
            for agency_data in agencies_data:
                # Extract agency name
                name_match = re.search(r'"name":"([^"]+)"', agency_data)
                name = name_match.group(1) if name_match else "Unknown"
                
                # Extract slug
                slug_match = re.search(r'"slug":"([^"]+)"', agency_data)
                slug = slug_match.group(1) if slug_match else "unknown"
                
                # Extract word count
                wordcount_match = re.search(r'"wordCount":(\d+)', agency_data)
                wordcount = int(wordcount_match.group(1)) if wordcount_match else 0
                
                # Extract section count
                sectioncount_match = re.search(r'"sectionCount":(\d+)', agency_data)
                sectioncount = int(sectioncount_match.group(1)) if sectioncount_match else 0
                
                inner_agencies.append({
                    "name": name,
                    "slug": slug,
                    "wordCount": wordcount,
                    "sectionCount": sectioncount
                })
            
            return inner_agencies
        except Exception as e2:
            print(f"Secondary parsing approach failed: {e2}")
            return None

def main():
    """Main function to process the Treasury HTML file"""
    print("Extracting inner agencies data from Department of Treasury HTML file...")
    
    inner_agencies = extract_agency_metrics("agency_treasury-department.html")
    
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