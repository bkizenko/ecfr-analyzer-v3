#!/usr/bin/env python3
import json
import re
from collections import defaultdict

# Agriculture Department inner agencies data from previous extraction
AGRICULTURE_INNER_AGENCIES_DATA = '''
[{"agency":{"id":"","name":"Agricultural Marketing Service","shortName":"","displayName":"","sortableName":"","slug":"agricultural-marketing-service","parent":null,"children":null,"cfr_references":[{"title":7},{"title":7},{"title":7},{"title":7},{"title":7},{"title":9}]},"metrics":{"wordCount":1483780,"sectionCount":8446}},{"agency":{"id":"","name":"Agricultural Research Service","shortName":"","displayName":"","sortableName":"","slug":"agricultural-research-service","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":18208,"sectionCount":116}},{"agency":{"id":"","name":"Animal and Plant Health Inspection Service","shortName":"","displayName":"","sortableName":"","slug":"animal-and-plant-health-inspection-service","parent":null,"children":null,"cfr_references":[{"title":7},{"title":9}]},"metrics":{"wordCount":895907,"sectionCount":1800}},{"agency":{"id":"","name":"Commodity Credit Corporation","shortName":"","displayName":"","sortableName":"","slug":"commodity-credit-corporation","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":463518,"sectionCount":1188}},{"agency":{"id":"","name":"Economic Research Service","shortName":"","displayName":"","sortableName":"","slug":"economic-research-service","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":3112,"sectionCount":11}},{"agency":{"id":"","name":"Farm Service Agency","shortName":"","displayName":"","sortableName":"","slug":"farm-service-agency","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":631608,"sectionCount":1797}},{"agency":{"id":"","name":"Federal Crop Insurance Corporation","shortName":"","displayName":"","sortableName":"","slug":"federal-crop-insurance-corporation","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":325539,"sectionCount":228}},{"agency":{"id":"","name":"Food and Nutrition Service","shortName":"","displayName":"","sortableName":"","slug":"food-and-nutrition-service","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":754841,"sectionCount":613}},{"agency":{"id":"","name":"Food Safety and Inspection Service","shortName":"","displayName":"","sortableName":"","slug":"food-safety-and-inspection-service","parent":null,"children":null,"cfr_references":[{"title":9}]},"metrics":{"wordCount":356866,"sectionCount":1085}},{"agency":{"id":"","name":"Foreign Agricultural Service","shortName":"","displayName":"","sortableName":"","slug":"foreign-agricultural-service","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":38642,"sectionCount":105}},{"agency":{"id":"","name":"Forest Service","shortName":"","displayName":"","sortableName":"","slug":"forest-service","parent":null,"children":null,"cfr_references":[{"title":36}]},"metrics":{"wordCount":321740,"sectionCount":706}},{"agency":{"id":"","name":"National Agricultural Statistics Service","shortName":"","displayName":"","sortableName":"","slug":"national-agricultural-statistics-service","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":2985,"sectionCount":11}},{"agency":{"id":"","name":"National Institute of Food and Agriculture","shortName":"","displayName":"","sortableName":"","slug":"national-institute-of-food-and-agriculture","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":109802,"sectionCount":353}},{"agency":{"id":"","name":"Natural Resources Conservation Service","shortName":"","displayName":"","sortableName":"","slug":"natural-resources-conservation-service","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":98231,"sectionCount":363}},{"agency":{"id":"","name":"Office of Advocacy and Outreach","shortName":"","displayName":"","sortableName":"","slug":"advocacy-and-outreach-office","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":9455,"sectionCount":50}},{"agency":{"id":"","name":"Office of Chief Financial Officer","shortName":"","displayName":"","sortableName":"","slug":"office-of-the-chief-financial-officer-agriculture-department","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":0,"sectionCount":0}},{"agency":{"id":"","name":"Office of Energy Policy and New Uses","shortName":"","displayName":"","sortableName":"","slug":"energy-policy-and-new-uses-office","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":6706,"sectionCount":37}},{"agency":{"id":"","name":"Office of Environmental Quality","shortName":"","displayName":"","sortableName":"","slug":"office-of-environmental-quality","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":2327,"sectionCount":7}},{"agency":{"id":"","name":"Office of Information Resources Management","shortName":"","displayName":"","sortableName":"","slug":"office-of-information-resources-management","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":1149,"sectionCount":8}},{"agency":{"id":"","name":"Office of Inspector General","shortName":"","displayName":"","sortableName":"","slug":"inspector-general-office-agriculture-department","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":2988,"sectionCount":10}},{"agency":{"id":"","name":"Office of Operations","shortName":"","displayName":"","sortableName":"","slug":"office-of-operations","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":2912,"sectionCount":19}},{"agency":{"id":"","name":"Office of Procurement and Property Management","shortName":"","displayName":"","sortableName":"","slug":"procurement-and-property-management-office-of","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":3077,"sectionCount":22}},{"agency":{"id":"","name":"Office of Secretary of Agriculture","shortName":"","displayName":"","sortableName":"","slug":"office-of-secretary-of-agriculture","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":0,"sectionCount":0}},{"agency":{"id":"","name":"Office of Transportation","shortName":"","displayName":"","sortableName":"","slug":"transportation-office","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":6658,"sectionCount":32}},{"agency":{"id":"","name":"Rural Business-Cooperative Service","shortName":"","displayName":"","sortableName":"","slug":"rural-business-cooperative-service","parent":null,"children":null,"cfr_references":[{"title":7},{"title":7},{"title":7}]},"metrics":{"wordCount":766081,"sectionCount":1734}},{"agency":{"id":"","name":"Rural Housing Service","shortName":"","displayName":"","sortableName":"","slug":"rural-housing-service","parent":null,"children":null,"cfr_references":[{"title":7},{"title":7},{"title":7}]},"metrics":{"wordCount":683443,"sectionCount":1600}},{"agency":{"id":"","name":"Rural Utilities Service","shortName":"","displayName":"","sortableName":"","slug":"rural-utilities-service","parent":null,"children":null,"cfr_references":[{"title":7},{"title":7},{"title":7},{"title":7}]},"metrics":{"wordCount":1158634,"sectionCount":2451}},{"agency":{"id":"","name":"World Agricultural Outlook Board","shortName":"","displayName":"","sortableName":"","slug":"world-agricultural-outlook-board","parent":null,"children":null,"cfr_references":[{"title":7}]},"metrics":{"wordCount":1227,"sectionCount":10}}]
'''

# Treasury Department inner agencies data from previous extraction
TREASURY_INNER_AGENCIES_DATA = '''
[{"agency":{"id":"","name":"Alcohol and Tobacco Tax and Trade Bureau","shortName":"","displayName":"","sortableName":"","slug":"alcohol-and-tobacco-tax-and-trade-bureau","parent":null,"children":null,"cfr_references":[{"title":27}]},"metrics":{"wordCount":901136,"sectionCount":3570}},{"agency":{"id":"","name":"Bureau of Engraving and Printing","shortName":"","displayName":"","sortableName":"","slug":"engraving-and-printing-bureau","parent":null,"children":null,"cfr_references":[{"title":31}]},"metrics":{"wordCount":8483,"sectionCount":59}},{"agency":{"id":"","name":"Bureau of the Fiscal Service","shortName":"","displayName":"","sortableName":"","slug":"fiscal-service-bureau-of","parent":null,"children":null,"cfr_references":[{"title":31}]},"metrics":{"wordCount":259307,"sectionCount":696}},{"agency":{"id":"","name":"Comptroller of the Currency","shortName":"","displayName":"","sortableName":"","slug":"comptroller-of-the-currency","parent":null,"children":null,"cfr_references":[{"title":12}]},"metrics":{"wordCount":839343,"sectionCount":2040}},{"agency":{"id":"","name":"Financial Crimes Enforcement Network","shortName":"","displayName":"","sortableName":"","slug":"financial-crimes-enforcement-network","parent":null,"children":null,"cfr_references":[{"title":31}]},"metrics":{"wordCount":95288,"sectionCount":204}},{"agency":{"id":"","name":"Internal Revenue Service","shortName":"","displayName":"","sortableName":"","slug":"internal-revenue-service","parent":null,"children":null,"cfr_references":[{"title":26},{"title":27},{"title":31}]},"metrics":{"wordCount":13013629,"sectionCount":28022}},{"agency":{"id":"","name":"United States Mint","shortName":"","displayName":"","sortableName":"","slug":"mint-bureau","parent":null,"children":null,"cfr_references":[{"title":31}]},"metrics":{"wordCount":2427,"sectionCount":34}}]
'''

# Additional Treasury Department data from the screenshot
TREASURY_WEBSITE_DATA = {
    "Alcohol and Tobacco Tax and Trade Bureau": {"wordCount": 901136, "sectionCount": 3570},
    "Comptroller of the Currency": {"wordCount": 740350, "sectionCount": 1120},
    "Office of Foreign Assets Control": {"wordCount": 559020, "sectionCount": 2710},
    "Fiscal Service": {"wordCount": 338270, "sectionCount": 1180},
    "Bureau of the Fiscal Service": {"wordCount": 338260, "sectionCount": 1180},
    "Financial Crimes Enforcement Network": {"wordCount": 101030, "sectionCount": 290},
    "Office of Investment Security": {"wordCount": 87540, "sectionCount": 287},
    "Community Development Financial Institutions Fund": {"wordCount": 50460, "sectionCount": 166},
    "Monetary Offices": {"wordCount": 29020, "sectionCount": 95},
    "Office of Financial Research": {"wordCount": 6050, "sectionCount": 7},
    "Bureau of Engraving and Printing": {"wordCount": 2820, "sectionCount": 6},
    "Internal Revenue Service": {"wordCount": 0, "sectionCount": 0},
    "Office of Secretary of the Treasury": {"wordCount": 0, "sectionCount": 0}
}

def fix_number_format(num_str):
    """Convert number strings like "901.14K" to integers like 901140"""
    if isinstance(num_str, int):
        return num_str
    
    num_str = str(num_str)
    
    # Remove commas if present
    num_str = num_str.replace(',', '')
    
    if 'K' in num_str:
        return int(float(num_str.replace('K', '')) * 1000)
    elif 'M' in num_str:
        return int(float(num_str.replace('M', '')) * 1000000)
    else:
        try:
            return int(float(num_str))
        except ValueError:
            return 0

def clean_agency_data(agency_json, parent_name, website_data=None):
    """Clean and harmonize agency data"""
    try:
        agencies = json.loads(agency_json)
        
        cleaned_agencies = []
        for agency in agencies:
            agency_info = agency.get('agency', {})
            metrics_data = agency.get('metrics', {})
            
            name = agency_info.get('name', 'Unknown')
            
            # If we have website data for this agency, use it to validate/update
            if website_data and name in website_data:
                # If our data shows 0 but website has a value, use website value
                if metrics_data.get('wordCount', 0) == 0 and website_data[name]['wordCount'] > 0:
                    metrics_data['wordCount'] = website_data[name]['wordCount']
                    metrics_data['sectionCount'] = website_data[name]['sectionCount']
                # If there's a big discrepancy (> 20%), log it
                elif metrics_data.get('wordCount', 0) > 0 and abs(metrics_data.get('wordCount', 0) - website_data[name]['wordCount']) / metrics_data.get('wordCount', 1) > 0.2:
                    print(f"Warning: Discrepancy in {name} word count: {metrics_data.get('wordCount', 0)} vs {website_data[name]['wordCount']}")
            
            # Special case for Internal Revenue Service showing 0 in the UI but actually has data
            if name == "Internal Revenue Service" and metrics_data.get('wordCount', 0) == 0:
                print(f"Fixing IRS data - replacing 0 with actual data")
                # Keep our extracted data for IRS since website shows 0
            
            cleaned_agencies.append({
                'name': name,
                'slug': agency_info.get('slug', ''),
                'cfr_references': agency_info.get('cfr_references', []),
                'wordCount': metrics_data.get('wordCount', 0),
                'sectionCount': metrics_data.get('sectionCount', 0),
                'parentAgency': parent_name
            })
        
        # Find agencies in website_data that aren't in our extracted data
        if website_data:
            extracted_names = {agency['name'] for agency in cleaned_agencies}
            for name, metrics in website_data.items():
                if name not in extracted_names and metrics['wordCount'] > 0:
                    print(f"Adding missing agency from website: {name}")
                    # Create slug from name
                    slug = name.lower().replace(' ', '-')
                    cleaned_agencies.append({
                        'name': name,
                        'slug': slug,
                        'cfr_references': [],
                        'wordCount': metrics['wordCount'],
                        'sectionCount': metrics['sectionCount'],
                        'parentAgency': parent_name
                    })
        
        # Sort by word count
        cleaned_agencies.sort(key=lambda x: x['wordCount'], reverse=True)
        return cleaned_agencies
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON data for {parent_name}: {e}")
        return []

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
    
    # Top parent agencies by word count
    print("Parent Agencies by Word Count:")
    for i, (parent, totals) in enumerate(sorted_parents):
        print(f"{i+1}. {parent}: {totals['totalWordCount']:,} words, {totals['innerAgencyCount']} inner agencies")
    
    # Generate Markdown report
    print("\nGenerating markdown report...")
    
    report = "# Inner Agencies Word Count Analysis (Cleaned Data)\n\n"
    
    report += "## Overview Statistics\n\n"
    report += f"- **Total Parent Agencies with Inner Agencies:** {len(agencies_by_parent)}\n"
    report += f"- **Total Inner Agencies:** {total_inner_agencies}\n"
    report += f"- **Total Inner Agencies Word Count:** {total_word_count:,}\n"
    report += f"- **Total Inner Agencies Section Count:** {total_section_count:,}\n\n"
    
    report += "## Top Inner Agencies by Word Count\n\n"
    report += "| Rank | Inner Agency | Parent Agency | Word Count | Section Count |\n"
    report += "|------|-------------|---------------|------------|---------------|\n"
    
    # Sort all inner agencies by word count
    all_inner_agencies_sorted = sorted(all_inner_agencies, key=lambda x: x['wordCount'], reverse=True)
    
    for i, agency in enumerate(all_inner_agencies_sorted):
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
    with open('inner_agencies_cleaned_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("Markdown report saved to inner_agencies_cleaned_report.md")
    
    # Save the raw data
    with open('inner_agencies_cleaned_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_inner_agencies, f, indent=2)
    
    print("Inner agencies data saved to inner_agencies_cleaned_data.json")
    
    # Create CSV version for easy import into spreadsheets
    with open('inner_agencies_cleaned_data.csv', 'w', encoding='utf-8') as f:
        f.write("Inner Agency,Parent Agency,Word Count,Section Count\n")
        for agency in all_inner_agencies_sorted:
            f.write(f"\"{agency['name']}\",\"{agency['parentAgency']}\",{agency['wordCount']},{agency['sectionCount']}\n")
    
    print("CSV version saved to inner_agencies_cleaned_data.csv")

def main():
    """Main function to clean and harmonize the inner agencies data"""
    print("Cleaning and harmonizing inner agencies data for Agriculture and Treasury departments...")
    
    all_inner_agencies = []
    
    # Process Treasury Department data with website data reconciliation
    treasury_agencies = clean_agency_data(TREASURY_INNER_AGENCIES_DATA, "Department of Treasury", TREASURY_WEBSITE_DATA)
    print(f"Processed {len(treasury_agencies)} inner agencies for Department of Treasury")
    all_inner_agencies.extend(treasury_agencies)
    
    # Process Agriculture Department (no website data to reconcile with)
    agriculture_agencies = clean_agency_data(AGRICULTURE_INNER_AGENCIES_DATA, "Department of Agriculture")
    print(f"Processed {len(agriculture_agencies)} inner agencies for Department of Agriculture")
    all_inner_agencies.extend(agriculture_agencies)
    
    # Generate report
    if all_inner_agencies:
        generate_report(all_inner_agencies)
    else:
        print("No inner agencies data found!")

if __name__ == "__main__":
    main() 