#!/usr/bin/env python3
import boto3
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_untagged_resources_in_region(region):
    untagged = []
    try:
        session = boto3.Session()
        
        # EC2 Instances
        ec2 = session.client('ec2', region_name=region)
        instances = ec2.describe_instances()
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                if not instance.get('Tags'):
                    untagged.append(f"EC2 Instance: {instance['InstanceId']}")
        
        # EBS Volumes
        volumes = ec2.describe_volumes()
        for volume in volumes['Volumes']:
            if not volume.get('Tags'):
                untagged.append(f"EBS Volume: {volume['VolumeId']}")
        
        # Lambda Functions
        lambda_client = session.client('lambda', region_name=region)
        functions = lambda_client.list_functions()
        for function in functions['Functions']:
            try:
                tags = lambda_client.list_tags(Resource=function['FunctionArn'])
                if not tags.get('Tags'):
                    untagged.append(f"Lambda Function: {function['FunctionName']}")
            except:
                untagged.append(f"Lambda Function: {function['FunctionName']}")
        
        # RDS Instances
        rds = session.client('rds', region_name=region)
        instances = rds.describe_db_instances()
        for instance in instances['DBInstances']:
            try:
                tags = rds.list_tags_for_resource(ResourceName=instance['DBInstanceArn'])
                if not tags.get('TagList'):
                    untagged.append(f"RDS Instance: {instance['DBInstanceIdentifier']}")
            except:
                untagged.append(f"RDS Instance: {instance['DBInstanceIdentifier']}")
        
        # VPCs
        vpcs = ec2.describe_vpcs()
        for vpc in vpcs['Vpcs']:
            if not vpc.get('Tags'):
                untagged.append(f"VPC: {vpc['VpcId']}")
        
        # Security Groups
        security_groups = ec2.describe_security_groups()
        for sg in security_groups['SecurityGroups']:
            if not sg.get('Tags'):
                untagged.append(f"Security Group: {sg['GroupId']}")
        
        # Subnets
        subnets = ec2.describe_subnets()
        for subnet in subnets['Subnets']:
            if not subnet.get('Tags'):
                untagged.append(f"Subnet: {subnet['SubnetId']}")
                
    except:
        pass
    
    return region, untagged

def main():
    session = boto3.Session()
    regions = [r['RegionName'] for r in session.client('ec2').describe_regions()['Regions']]
    
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = [executor.submit(get_untagged_resources_in_region, region) for region in regions]
        
        for future in as_completed(futures):
            region, untagged = future.result()
            if untagged:
                print(f"\n{region} ({len(untagged)} untagged resources):")
                for resource in untagged:
                    print(f"  - {resource}")
    
    # S3 Buckets (global)
    try:
        s3 = session.client('s3')
        buckets = s3.list_buckets()
        untagged_buckets = []
        for bucket in buckets['Buckets']:
            try:
                s3.get_bucket_tagging(Bucket=bucket['Name'])
            except:
                untagged_buckets.append(f"S3 Bucket: {bucket['Name']}")
        
        if untagged_buckets:
            print(f"\nGlobal S3 ({len(untagged_buckets)} untagged buckets):")
            for bucket in untagged_buckets:
                print(f"  - {bucket}")
    except:
        pass

if __name__ == "__main__":
    main()