#!/usr/bin/env python3
import boto3
import csv
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_untagged_resources_in_region(region, account_id):
    resources = []
    try:
        session = boto3.Session()
        
        # EC2 Instances
        ec2 = session.client('ec2', region_name=region)
        instances = ec2.describe_instances()
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                if not instance.get('Tags'):
                    resources.append({
                        'Account': account_id,
                        'Region': region,
                        'Resource': 'EC2 Instance',
                        'ARN': f"arn:aws:ec2:{region}:{account_id}:instance/{instance['InstanceId']}"
                    })
        
        # EBS Volumes
        volumes = ec2.describe_volumes()
        for volume in volumes['Volumes']:
            if not volume.get('Tags'):
                resources.append({
                    'Account': account_id,
                    'Region': region,
                    'Resource': 'EBS Volume',
                    'ARN': f"arn:aws:ec2:{region}:{account_id}:volume/{volume['VolumeId']}"
                })
        
        # VPCs
        vpcs = ec2.describe_vpcs()
        for vpc in vpcs['Vpcs']:
            if not vpc.get('Tags'):
                resources.append({
                    'Account': account_id,
                    'Region': region,
                    'Resource': 'VPC',
                    'ARN': f"arn:aws:ec2:{region}:{account_id}:vpc/{vpc['VpcId']}"
                })
        
        # Security Groups
        security_groups = ec2.describe_security_groups()
        for sg in security_groups['SecurityGroups']:
            if not sg.get('Tags'):
                resources.append({
                    'Account': account_id,
                    'Region': region,
                    'Resource': 'Security Group',
                    'ARN': f"arn:aws:ec2:{region}:{account_id}:security-group/{sg['GroupId']}"
                })
        
        # Subnets
        subnets = ec2.describe_subnets()
        for subnet in subnets['Subnets']:
            if not subnet.get('Tags'):
                resources.append({
                    'Account': account_id,
                    'Region': region,
                    'Resource': 'Subnet',
                    'ARN': f"arn:aws:ec2:{region}:{account_id}:subnet/{subnet['SubnetId']}"
                })
        
        # Lambda Functions
        lambda_client = session.client('lambda', region_name=region)
        functions = lambda_client.list_functions()
        for function in functions['Functions']:
            try:
                tags = lambda_client.list_tags(Resource=function['FunctionArn'])
                if not tags.get('Tags'):
                    resources.append({
                        'Account': account_id,
                        'Region': region,
                        'Resource': 'Lambda Function',
                        'ARN': function['FunctionArn']
                    })
            except:
                resources.append({
                    'Account': account_id,
                    'Region': region,
                    'Resource': 'Lambda Function',
                    'ARN': function['FunctionArn']
                })
        
        # RDS Instances
        rds = session.client('rds', region_name=region)
        instances = rds.describe_db_instances()
        for instance in instances['DBInstances']:
            try:
                tags = rds.list_tags_for_resource(ResourceName=instance['DBInstanceArn'])
                if not tags.get('TagList'):
                    resources.append({
                        'Account': account_id,
                        'Region': region,
                        'Resource': 'RDS Instance',
                        'ARN': instance['DBInstanceArn']
                    })
            except:
                resources.append({
                    'Account': account_id,
                    'Region': region,
                    'Resource': 'RDS Instance',
                    'ARN': instance['DBInstanceArn']
                })
                
    except:
        pass
    
    return resources

def main():
    session = boto3.Session()
    
    # Get account ID
    sts = session.client('sts')
    account_id = sts.get_caller_identity()['Account']
    
    # Get regions
    regions = [r['RegionName'] for r in session.client('ec2').describe_regions()['Regions']]
    
    all_resources = []
    
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = [executor.submit(get_untagged_resources_in_region, region, account_id) for region in regions]
        
        for future in as_completed(futures):
            resources = future.result()
            all_resources.extend(resources)
    
    # S3 Buckets (global)
    try:
        s3 = session.client('s3')
        buckets = s3.list_buckets()
        for bucket in buckets['Buckets']:
            try:
                s3.get_bucket_tagging(Bucket=bucket['Name'])
            except:
                all_resources.append({
                    'Account': account_id,
                    'Region': 'Global',
                    'Resource': 'S3 Bucket',
                    'ARN': f"arn:aws:s3:::{bucket['Name']}"
                })
    except:
        pass
    
    # Create output directory and filename
    os.makedirs('output', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'output/untagged_resources_{timestamp}.csv'
    
    # Export to CSV
    if all_resources:
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['Account', 'Region', 'Resource', 'ARN']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_resources)
        print(f"Exported {len(all_resources)} untagged resources to {filename}")
    else:
        print("No untagged resources found")

if __name__ == "__main__":
    main()