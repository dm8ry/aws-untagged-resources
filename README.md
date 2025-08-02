# AWS Resource Management Scripts

Python scripts to analyze untagged AWS resources across all regions.

## Scripts

### `get_untagged_resources_per_region.py`
List all untagged resources grouped by region (console output).
```bash
python get_untagged_resources_per_region.py
```

### `get_untagged_resources_per_region_excel.py`
Export untagged resources to CSV with account, region, resource type, and ARN.
```bash
python get_untagged_resources_per_region_excel.py
```
Output: `output/untagged_resources_YYYYMMDD_HHMMSS.csv`

### `advanced_analysis.py`
Analyze exported CSV data without external dependencies.
```bash
python advanced_analysis.py
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure AWS credentials:
```bash
aws configure
```

## Required Permissions

- `ec2:DescribeInstances`
- `ec2:DescribeVolumes`
- `ec2:DescribeVpcs`
- `ec2:DescribeSecurityGroups`
- `ec2:DescribeSubnets`
- `s3:ListAllMyBuckets`
- `s3:GetBucketTagging`
- `lambda:ListFunctions`
- `lambda:ListTags`
- `rds:DescribeDBInstances`
- `rds:ListTagsForResource`

## Supported Resources

- EC2 Instances
- EBS Volumes
- VPCs
- Security Groups
- Subnets
- S3 Buckets
- Lambda Functions
- RDS Instances