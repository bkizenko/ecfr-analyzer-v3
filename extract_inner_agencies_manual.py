#!/usr/bin/env python3
import json
from collections import defaultdict

# Direct extraction of inner agencies data from Agriculture Department
AGRICULTURE_INNER_AGENCIES_DATA = '''
[{"agency":{"id":"","name":"Agricultural Marketing Service","shortName":"","displayName":"","sortableName":"","slug":"agricultural-marketing-service","parent":null,"children":null,"cfr_references":[{"title":7},{"title":7},{"title":7},{"title":7},{"title":7},{"title":9}]},"metrics":{"wordCount":1483780,"sectionCount":8446}},{"agency":{"id":"","name":"Agricultural Research Service","shortName":"","displayName":"","sortableName":"","slug":"agricultural-research-service","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":18208,"sectionCount":116}},{"agency":{"id":"","name":"Animal and Plant Health Inspection Service","shortName":"","displayName":"","sortableName":"","slug":"animal-and-plant-health-inspection-service","parent":null,"children":null,"cfr_references":[{"title":7},{"title":9}]},"metrics":{"wordCount":895907,"sectionCount":1800}},{"agency":{"id":"","name":"Commodity Credit Corporation","shortName":"","displayName":"","sortableName":"","slug":"commodity-credit-corporation","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":463518,"sectionCount":1188}},{"agency":{"id":"","name":"Economic Research Service","shortName":"","displayName":"","sortableName":"","slug":"economic-research-service","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":3112,"sectionCount":11}},{"agency":{"id":"","name":"Farm Service Agency","shortName":"","displayName":"","sortableName":"","slug":"farm-service-agency","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":631608,"sectionCount":1797}},{"agency":{"id":"","name":"Federal Crop Insurance Corporation","shortName":"","displayName":"","sortableName":"","slug":"federal-crop-insurance-corporation","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":325539,"sectionCount":228}},{"agency":{"id":"","name":"Food and Nutrition Service","shortName":"","displayName":"","sortableName":"","slug":"food-and-nutrition-service","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":754841,"sectionCount":613}},{"agency":{"id":"","name":"Food Safety and Inspection Service","shortName":"","displayName":"","sortableName":"","slug":"food-safety-and-inspection-service","parent":null,"children":null,"cfr_references":[{"title":9}]},"metrics":{"wordCount":356866,"sectionCount":1085}},{"agency":{"id":"","name":"Foreign Agricultural Service","shortName":"","displayName":"","sortableName":"","slug":"foreign-agricultural-service","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":38642,"sectionCount":105}},{"agency":{"id":"","name":"Forest Service","shortName":"","displayName":"","sortableName":"","slug":"forest-service","parent":null,"children":null,"cfr_references":[{"title":36}]},"metrics":{"wordCount":321740,"sectionCount":706}},{"agency":{"id":"","name":"National Agricultural Statistics Service","shortName":"","displayName":"","sortableName":"","slug":"national-agricultural-statistics-service","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":2985,"sectionCount":11}},{"agency":{"id":"","name":"National Institute of Food and Agriculture","shortName":"","displayName":"","sortableName":"","slug":"national-institute-of-food-and-agriculture","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":109802,"sectionCount":353}},{"agency":{"id":"","name":"Natural Resources Conservation Service","shortName":"","displayName":"","sortableName":"","slug":"natural-resources-conservation-service","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":98231,"sectionCount":363}},{"agency":{"id":"","name":"Office of Advocacy and Outreach","shortName":"","displayName":"","sortableName":"","slug":"advocacy-and-outreach-office","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":9455,"sectionCount":50}},{"agency":{"id":"","name":"Office of Chief Financial Officer","shortName":"","displayName":"","sortableName":"","slug":"office-of-the-chief-financial-officer-agriculture-department","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":0,"sectionCount":0}},{"agency":{"id":"","name":"Office of Energy Policy and New Uses","shortName":"","displayName":"","sortableName":"","slug":"energy-policy-and-new-uses-office","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":6706,"sectionCount":37}},{"agency":{"id":"","name":"Office of Environmental Quality","shortName":"","displayName":"","sortableName":"","slug":"office-of-environmental-quality","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":2327,"sectionCount":7}},{"agency":{"id":"","name":"Office of Information Resources Management","shortName":"","displayName":"","sortableName":"","slug":"office-of-information-resources-management","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":1149,"sectionCount":8}},{"agency":{"id":"","name":"Office of Inspector General","shortName":"","displayName":"","sortableName":"","slug":"inspector-general-office-agriculture-department","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":2988,"sectionCount":10}},{"agency":{"id":"","name":"Office of Operations","shortName":"","displayName":"","sortableName":"","slug":"office-of-operations","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":2912,"sectionCount":19}},{"agency":{"id":"","name":"Office of Procurement and Property Management","shortName":"","displayName":"","sortableName":"","slug":"procurement-and-property-management-office-of","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":3077,"sectionCount":22}},{"agency":{"id":"","name":"Office of Secretary of Agriculture","shortName":"","displayName":"","sortableName":"","slug":"office-of-secretary-of-agriculture","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":0,"sectionCount":0}},{"agency":{"id":"","name":"Office of Transportation","shortName":"","displayName":"","sortableName":"","slug":"transportation-office","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":6658,"sectionCount":32}},{"agency":{"id":"","name":"Rural Business-Cooperative Service","shortName":"","displayName":"","sortableName":"","slug":"rural-business-cooperative-service","parent":null,"children":null,"cfr_references":[{"title":7},{"title":7},{"title":7}]},"metrics":{"wordCount":766081,"sectionCount":1734}},{"agency":{"id":"","name":"Rural Housing Service","shortName":"","displayName":"","sortableName":"","slug":"rural-housing-service","parent":null,"children":null,"cfr_references":[{"title":7},{"title":7},{"title":7}]},"metrics":{"wordCount":683443,"sectionCount":1600}},{"agency":{"id":"","name":"Rural Utilities Service","shortName":"","displayName":"","sortableName":"","slug":"rural-utilities-service","parent":null,"children":null,"cfr_references":[{"title":7},{"title":7},{"title":7},{"title":7}]},"metrics":{"wordCount":1158634,"sectionCount":2451}},{"agency":{"id":"","name":"World Agricultural Outlook Board","shortName":"","displayName":"","sortableName":"","slug":"world-agricultural-outlook-board","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":1227,"sectionCount":10}}]
'''

# Treasury Department data
TREASURY_INNER_AGENCIES_DATA = '''
[{"agency":{"id":"","name":"Alcohol and Tobacco Tax and Trade Bureau","shortName":"","displayName":"","sortableName":"","slug":"alcohol-and-tobacco-tax-and-trade-bureau","parent":null,"children":null,"cfr_references":[{"title":27}]},"metrics":{"wordCount":901136,"sectionCount":3570}},{"agency":{"id":"","name":"Bureau of Engraving and Printing","shortName":"","displayName":"","sortableName":"","slug":"engraving-and-printing-bureau","parent":null,"children":null,"cfr_references":[{"title":31}]},"metrics":{"wordCount":8483,"sectionCount":59}},{"agency":{"id":"","name":"Bureau of the Fiscal Service","shortName":"","displayName":"","sortableName":"","slug":"fiscal-service-bureau-of","parent":null,"children":null,"cfr_references":[{"title":31}]},"metrics":{"wordCount":259307,"sectionCount":696}},{"agency":{"id":"","name":"Comptroller of the Currency","shortName":"","displayName":"","sortableName":"","slug":"comptroller-of-the-currency","parent":null,"children":null,"cfr_references":[{"title":12}]},"metrics":{"wordCount":839343,"sectionCount":2040}},{"agency":{"id":"","name":"Financial Crimes Enforcement Network","shortName":"","displayName":"","sortableName":"","slug":"financial-crimes-enforcement-network","parent":null,"children":null,"cfr_references":[{"title":31}]},"metrics":{"wordCount":95288,"sectionCount":204}},{"agency":{"id":"","name":"Internal Revenue Service","shortName":"","displayName":"","sortableName":"","slug":"internal-revenue-service","parent":null,"children":null,"cfr_references":[{"title":26},{"title":27},{"title":31}]},"metrics":{"wordCount":13013629,"sectionCount":28022}},{"agency":{"id":"","name":"United States Mint","shortName":"","displayName":"","sortableName":"","slug":"mint-bureau","parent":null,"children":null,"cfr_references":[{"title":31}]},"metrics":{"wordCount":2427,"sectionCount":34}}]
'''

def process_inner_agencies_data():
    """Process the inner agencies data"""
    # Create the data to process
    agency_data = [
        {"agency_name": "Department of Agriculture", "slug": "agriculture-department", "data": AGRICULTURE_INNER_AGENCIES_DATA},
        {"agency_name": "Department of Treasury", "slug": "treasury-department", "data": TREASURY_INNER_AGENCIES_DATA}
    ]
    
    all_inner_agencies = []
    
    # Process each agency's data
    for agency in agency_data:
        parent_agency_name = agency["agency_name"]
        parent_agency_slug = agency["slug"]
        data_string = agency["data"]
        
        try:
            # Parse the JSON data
            metrics = json.loads(data_string)
            
            # Format the data
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
            
            # Add to the global list
            all_inner_agencies.extend(inner_agencies)
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON data for {parent_agency_name}: {e}")
    
    return all_inner_agencies

def generate_report(all_inner_agencies):
    """Generate a report for the inner agencies data"""
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
    
    # Print statistics
    print("\n=== INNER AGENCIES STATISTICS ===")
    print(f"Total Inner Agencies: {total_inner_agencies}")
    print(f"Total Word Count: {total_word_count:,}")
    print(f"Total Section Count: {total_section_count:,}\n")
    
    print("Parent Agency Word Counts (sorted by total words in inner agencies):")
    for parent, totals in sorted_parents:
        print(f"{parent}: {totals['totalWordCount']:,} words, {totals['innerAgencyCount']} inner agencies")
    
    # Generate report in Markdown format
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
    
    # Save the report to a file
    with open('inner_agencies_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("\nMarkdown report saved to inner_agencies_report.md")
    
    # Save the inner agencies data
    with open('inner_agencies_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_inner_agencies, f, indent=2)
    
    print("Inner agencies data saved to inner_agencies_data.json")

def main():
    """Main function to process and report on inner agencies data"""
    print("Processing inner agencies data...")
    all_inner_agencies = process_inner_agencies_data()
    
    if all_inner_agencies:
        generate_report(all_inner_agencies)
    else:
        print("No inner agencies data found!")

if __name__ == "__main__":
    main() 