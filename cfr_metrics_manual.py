#!/usr/bin/env python3
import json

# The total metrics we had previously found
total_metrics = {
    "totalWordCount": 104372225,
    "totalSectionCount": 231304,
    "totalAgencyCount": 153,
    "totalInnerAgencyCount": 163
}

# Agency data from our previous collection
agency_data = [
    {"name": "Department of Treasury", "wordCount": 15120613, "sectionCount": 16768},
    {"name": "Department of Agriculture", "wordCount": 13566594, "sectionCount": 39902},
    {"name": "Department of Health and Human Services", "wordCount": 7868232, "sectionCount": 20262},
    {"name": "Department of Transportation", "wordCount": 5677323, "sectionCount": 13577},
    {"name": "Department of Homeland Security", "wordCount": 4942784, "sectionCount": 16066},
    {"name": "Department of Interior", "wordCount": 4405024, "sectionCount": 13673},
    {"name": "Department of Labor", "wordCount": 4310871, "sectionCount": 10129},
    {"name": "Department of Commerce", "wordCount": 3887599, "sectionCount": 5350},
    {"name": "Department of Defense", "wordCount": 3361009, "sectionCount": 6755},
    {"name": "Department of Housing and Urban Development", "wordCount": 2536007, "sectionCount": 7001},
    {"name": "Environmental Protection Agency", "wordCount": 2526348, "sectionCount": 10986},
    {"name": "Department of Energy", "wordCount": 2321198, "sectionCount": 7252},
    {"name": "Federal Communications Commission", "wordCount": 2029617, "sectionCount": 3764},
    {"name": "Department of Education", "wordCount": 1972177, "sectionCount": 5178},
    {"name": "Department of Justice", "wordCount": 1927095, "sectionCount": 3947},
    {"name": "Securities and Exchange Commission", "wordCount": 1886962, "sectionCount": 1746},
    {"name": "Federal Aviation Administration", "wordCount": 1830348, "sectionCount": 1778},
    {"name": "Department of Veterans Affairs", "wordCount": 1697339, "sectionCount": 4225},
    {"name": "Government Accountability Office", "wordCount": 1572733, "sectionCount": 2062},
    {"name": "Federal Deposit Insurance Corporation", "wordCount": 1474219, "sectionCount": 2082},
    {"name": "Corporation for National and Community Service", "wordCount": 1333517, "sectionCount": 1487},
    {"name": "Small Business Administration", "wordCount": 1299341, "sectionCount": 2371},
    {"name": "Office of Personnel Management", "wordCount": 1196254, "sectionCount": 2511},
    {"name": "Postal Service", "wordCount": 1191358, "sectionCount": 3190},
    {"name": "Internal Revenue Service", "wordCount": 1151969, "sectionCount": 1067},
    {"name": "Nuclear Regulatory Commission", "wordCount": 1145879, "sectionCount": 2260},
    {"name": "Federal Reserve System", "wordCount": 1125387, "sectionCount": 1304},
    {"name": "Commodity Futures Trading Commission", "wordCount": 879969, "sectionCount": 2138},
    {"name": "Federal Trade Commission", "wordCount": 873347, "sectionCount": 989},
    {"name": "Consumer Financial Protection Bureau", "wordCount": 808462, "sectionCount": 758}
]

# Treasury Department sub-agencies from the screenshot
treasury_inner_agencies = [
    {"name": "Internal Revenue Service", "wordCount": 8642335, "sectionCount": 10062},
    {"name": "Office of the Comptroller of the Currency", "wordCount": 1833257, "sectionCount": 1635},
    {"name": "Department of the Treasury", "wordCount": 1151969, "sectionCount": 1067},
    {"name": "Alcohol and Tobacco Tax and Trade Bureau", "wordCount": 760972, "sectionCount": 962},
    {"name": "Office of Foreign Assets Control", "wordCount": 596423, "sectionCount": 1062},
    {"name": "Fiscal Service", "wordCount": 462918, "sectionCount": 455},
    {"name": "Office of Investment Security", "wordCount": 290551, "sectionCount": 208},
    {"name": "Financial Crimes Enforcement Network", "wordCount": 198355, "sectionCount": 187},
    {"name": "Community Development Financial Institutions Fund", "wordCount": 185284, "sectionCount": 120},
    {"name": "Internal Revenue Service. Art Advisory Panel", "wordCount": 5345, "sectionCount": 1}
]

def print_metrics():
    print("\n# CFR Metrics Summary")
    print(f"\n## Overall Totals")
    print(f"- Total Words: {total_metrics['totalWordCount']:,}")
    print(f"- Total Sections: {total_metrics['totalSectionCount']:,}")
    print(f"- Total Agencies: {total_metrics['totalAgencyCount']:,}")
    print(f"- Total Inner Agencies: {total_metrics['totalInnerAgencyCount']:,}")
    
    print("\n## Top 30 Agencies by Word Count")
    print("| Agency | Word Count | Section Count |")
    print("|--------|------------|---------------|")
    for agency in agency_data:
        print(f"| {agency['name']} | {agency['wordCount']:,} | {agency['sectionCount']:,} |")
    
    print("\n## Department of Treasury Inner Agencies")
    print("| Inner Agency | Word Count | Section Count |")
    print("|-------------|------------|---------------|")
    for agency in treasury_inner_agencies:
        print(f"| {agency['name']} | {agency['wordCount']:,} | {agency['sectionCount']:,} |")

if __name__ == "__main__":
    print_metrics()
    
    # Save to a json file as well
    with open('cfr_metrics_data.json', 'w') as f:
        json.dump({
            "totalMetrics": total_metrics,
            "topAgencies": agency_data,
            "treasuryInnerAgencies": treasury_inner_agencies
        }, f, indent=2)
    
    print("\nData also saved to cfr_metrics_data.json") 