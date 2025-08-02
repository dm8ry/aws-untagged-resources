#!/usr/bin/env python3
import csv
from collections import Counter

def analyze_csv(filename):
    """Analyze untagged resources CSV without pandas"""
    resources = []
    
    try:
        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            resources = list(reader)
    except FileNotFoundError:
        print(f"File {filename} not found")
        return
    
    if not resources:
        print("No data found in CSV")
        return
    
    print(f"Total untagged resources: {len(resources)}")
    
    # Count by resource type
    resource_counts = Counter(row['Resource'] for row in resources)
    print("\nResources by type:")
    for resource_type, count in resource_counts.most_common():
        print(f"  {resource_type}: {count}")
    
    # Count by region
    region_counts = Counter(row['Region'] for row in resources)
    print("\nResources by region:")
    for region, count in region_counts.most_common():
        print(f"  {region}: {count}")
    
    # Filter EC2 instances
    ec2_instances = [row for row in resources if row['Resource'] == 'EC2 Instance']
    if ec2_instances:
        print(f"\nEC2 Instances ({len(ec2_instances)}):")
        for instance in ec2_instances[:5]:  # Show first 5
            print(f"  {instance['Region']}: {instance['ARN']}")
        if len(ec2_instances) > 5:
            print(f"  ... and {len(ec2_instances) - 5} more")

if __name__ == "__main__":
    # Find the latest CSV file
    import os
    import glob
    
    csv_files = glob.glob('output/untagged_resources_*.csv')
    if csv_files:
        latest_file = max(csv_files, key=os.path.getctime)
        print(f"Analyzing: {latest_file}\n")
        analyze_csv(latest_file)
    else:
        print("No CSV files found in output/ directory")
        print("Run get_untagged_resources_per_region_excel.py first")