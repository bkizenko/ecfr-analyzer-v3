#!/usr/bin/env python3
import json

def process_treasury_agencies():
    """Process and display Treasury inner agencies data"""
    print("Processing Treasury inner agencies data...")
    
    # Load the data from the JSON file
    with open('treasury_agencies_data.json', 'r') as f:
        agencies_data = json.load(f)
    
    # Extract the relevant data and sort by word count
    agencies = []
    for item in agencies_data:
        agency_info = item['agency']
        metrics = item['metrics']
        
        agencies.append({
            'name': agency_info['name'],
            'slug': agency_info['slug'],
            'wordCount': metrics['wordCount'],
            'sectionCount': metrics['sectionCount'],
            'references': agency_info['cfr_references'][0]['title'] if agency_info['cfr_references'] else None
        })
    
    # Sort by word count (descending)
    agencies.sort(key=lambda x: x['wordCount'], reverse=True)
    
    # Print a markdown table of the results
    print("\n## Department of Treasury Inner Agencies by Word Count")
    print("| Rank | Inner Agency | Word Count | Section Count | CFR Title |")
    print("|------|-------------|------------|---------------|-----------|")
    for i, agency in enumerate(agencies):
        print(f"| {i+1} | {agency['name']} | {agency['wordCount']:,} | {agency['sectionCount']:,} | {agency['references']} |")
    
    # Calculate total word count and section count
    total_word_count = sum(agency['wordCount'] for agency in agencies)
    total_section_count = sum(agency['sectionCount'] for agency in agencies)
    
    print(f"\nTotal Word Count: {total_word_count:,}")
    print(f"Total Section Count: {total_section_count:,}")
    
    # Save the processed data to a new JSON file
    with open('treasury_inner_agencies_processed.json', 'w') as f:
        json.dump(agencies, f, indent=2)
    
    print("\nProcessed data saved to treasury_inner_agencies_processed.json")

if __name__ == "__main__":
    process_treasury_agencies() 