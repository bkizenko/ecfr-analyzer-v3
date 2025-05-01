#!/usr/bin/env python3
import re
import json
from collections import defaultdict

def extract_all_agencies():
    """Extract all agencies and their inner agencies from the homepage HTML"""
    
    print("Extracting agencies data from HTML...")
    
    try:
        with open('agencies/homepage.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Extract all agency data from the HTML using regex
        pattern = r'"agency":\s*({.*?}),\s*"metrics":\s*({.*?})'
        matches = re.findall(pattern, html_content, re.DOTALL)
        
        if not matches:
            print("Could not find agency data in the HTML")
            return None
        
        # Process the extracted data
        all_agencies = []
        parent_agencies = []
        inner_agencies_map = defaultdict(list)
        
        for agency_str, metrics_str in matches:
            try:
                # Fix JSON format for parsing
                agency_str = agency_str.replace("'", '"').replace('\\"', '"')
                metrics_str = metrics_str.replace("'", '"')
                
                # Parse the JSON data
                agency = json.loads(agency_str)
                metrics = json.loads(metrics_str)
                
                # Create agency data structure
                agency_data = {
                    'name': agency.get('name', 'Unknown'),
                    'slug': agency.get('slug', ''),
                    'shortName': agency.get('shortName', ''),
                    'wordCount': metrics.get('wordCount', 0),
                    'sectionCount': metrics.get('sectionCount', 0),
                    'children': []
                }
                
                # Check if this agency has children (inner agencies)
                children = agency.get('children', [])
                if children and isinstance(children, list) and len(children) > 0 and children[0] is not None:
                    parent_agencies.append(agency_data)
                    
                    # Store inner agencies for this parent
                    for child in children:
                        if child:
                            inner_agency = {
                                'name': child.get('name', 'Unknown'),
                                'slug': child.get('slug', ''),
                                'cfr_references': child.get('cfr_references', [])
                            }
                            inner_agencies_map[agency_data['name']].append(inner_agency)
                
                all_agencies.append(agency_data)
            
            except Exception as e:
                print(f"Error processing agency data: {e}")
                continue
        
        # Sort agencies by word count (descending)
        all_agencies.sort(key=lambda x: x['wordCount'], reverse=True)
        parent_agencies.sort(key=lambda x: x['wordCount'], reverse=True)
        
        # Add inner agencies to their parent agencies
        for parent in parent_agencies:
            parent['children'] = inner_agencies_map.get(parent['name'], [])
        
        # Save all agencies to a file
        with open('all_agencies.json', 'w') as f:
            json.dump(all_agencies, f, indent=2)
        
        # Save parent agencies with their inner agencies
        with open('parent_agencies_with_inner.json', 'w') as f:
            json.dump(parent_agencies, f, indent=2)
        
        # Create summary statistics
        total_word_count = sum(agency['wordCount'] for agency in all_agencies)
        total_section_count = sum(agency['sectionCount'] for agency in all_agencies)
        total_agencies = len(all_agencies)
        total_parent_agencies = len(parent_agencies)
        total_inner_agencies = sum(len(agency['children']) for agency in parent_agencies)
        
        summary = {
            'total_word_count': total_word_count,
            'total_section_count': total_section_count,
            'total_agencies': total_agencies,
            'total_parent_agencies': total_parent_agencies,
            'total_inner_agencies': total_inner_agencies
        }
        
        with open('agencies_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Create a simple report
        print(f"\nTotal Word Count: {total_word_count:,}")
        print(f"Total Section Count: {total_section_count:,}")
        print(f"Total Agencies: {total_agencies}")
        print(f"Parent Agencies: {total_parent_agencies}")
        print(f"Inner Agencies: {total_inner_agencies}")
        
        print("\nTop 10 Agencies by Word Count:")
        for i, agency in enumerate(all_agencies[:10]):
            print(f"{i+1}. {agency['name']}: {agency['wordCount']:,} words")
        
        return all_agencies, parent_agencies
    
    except Exception as e:
        print(f"Error extracting agency data: {e}")
        return None

def main():
    """Main function to extract and display agency data"""
    print("Starting extraction of agency data...")
    
    # Extract agency data
    agencies_data = extract_all_agencies()
    
    if not agencies_data:
        print("\nFailed to extract agency data")
        return
    
    print("\nAgency data extraction completed successfully")
    print("Results saved to all_agencies.json, parent_agencies_with_inner.json, and agencies_summary.json")

if __name__ == "__main__":
    main() 