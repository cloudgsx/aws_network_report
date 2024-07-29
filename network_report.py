import boto3
import csv
from botocore.exceptions import ClientError

# Initialize the boto3 client for STS and Organizations
sts_client = boto3.client('sts')
org_client = boto3.client('organizations')

# Function to assume a role in a given account
def assume_role(account_id, role_name):
    response = sts_client.assume_role(
        RoleArn=f'arn:aws:iam::{account_id}:role/{role_name}',
        RoleSessionName='AssumeRoleSession'
    )
    credentials = response['Credentials']
    return boto3.Session(
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )

# Function to list all subnets in an account
def list_subnets(ec2_client):
    try:
        subnets = ec2_client.describe_subnets()['Subnets']
        return subnets
    except ClientError as e:
        print(f"Error describing subnets: {e}")
        return []

# Function to get resource details for a given subnet
def get_resources_in_subnet(ec2_client, rds_client, elbv2_client, subnet_id):
    ec2_resources = []
    try:
        ec2_instances = ec2_client.describe_instances(
            Filters=[{'Name': 'subnet-id', 'Values': [subnet_id]}]
        )
        for reservation in ec2_instances['Reservations']:
            for instance in reservation['Instances']:
                ec2_resources.append({
                    'InstanceId': instance['InstanceId'],
                    'InstanceType': instance['InstanceType'],
                    'State': instance['State']['Name']
                })
    except ClientError as e:
        print(f"Error describing EC2 instances in subnet {subnet_id}: {e}")

    rds_resources = []
    try:
        rds_instances = rds_client.describe_db_instances()
        for db_instance in rds_instances['DBInstances']:
            for subnet in db_instance['DBSubnetGroup']['Subnets']:
                if subnet['SubnetIdentifier'] == subnet_id:
                    rds_resources.append({
                        'DBInstanceIdentifier': db_instance['DBInstanceIdentifier'],
                        'DBInstanceClass': db_instance['DBInstanceClass'],
                        'Engine': db_instance['Engine']
                    })
    except ClientError as e:
        print(f"Error describing RDS instances in subnet {subnet_id}: {e}")

    elb_resources = []
    try:
        elbv2_load_balancers = elbv2_client.describe_load_balancers()
        for elb in elbv2_load_balancers['LoadBalancers']:
            for availability_zone in elb['AvailabilityZones']:
                if availability_zone['SubnetId'] == subnet_id:
                    elb_resources.append({
                        'LoadBalancerName': elb['LoadBalancerName'],
                        'Type': elb['Type'],
                        'State': elb['State']['Code']
                    })
    except ClientError as e:
        print(f"Error describing ELBv2 load balancers in subnet {subnet_id}: {e}")

    return {
        'EC2Instances': ec2_resources,
        'RDSInstances': rds_resources,
        'LoadBalancers': elb_resources
    }

# Function to write the report to a CSV file
def write_report(report_data):
    with open('subnets_report.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['AccountId', 'SubnetId', 'CIDR', 'AvailableIPs', 'ResourceType', 'ResourceId', 'ResourceDetails'])

        for account_data in report_data:
            for subnet in account_data['Subnets']:
                for resource_type, resources in subnet['Resources'].items():
                    for resource in resources:
                        writer.writerow([
                            account_data['AccountId'],
                            subnet['SubnetId'],
                            subnet['CIDR'],
                            subnet['AvailableIpAddressCount'],
                            resource_type,
                            resource.get('InstanceId') or resource.get('DBInstanceIdentifier') or resource.get('LoadBalancerName'),
                            resource
                        ])

def main():
    # Get the list of all accounts in the organization
    paginator = org_client.get_paginator('list_accounts')
    account_ids = []
    for page in paginator.paginate():
        for account in page['Accounts']:
            if account['Status'] == 'ACTIVE':
                account_ids.append(account['Id'])

    role_name = 'YOUR_ROLE_TO_ASSUME'
    report_data = []

    for account_id in account_ids:
        print(f"Processing account: {account_id}")
        try:
            session = assume_role(account_id, role_name)
        except ClientError as e:
            print(f"Error assuming role in account {account_id}: {e}")
            continue

        ec2_client = session.client('ec2')
        rds_client = session.client('rds')
        elbv2_client = session.client('elbv2')

        subnets = list_subnets(ec2_client)
        if not subnets:
            continue

        account_report = {
            'AccountId': account_id,
            'Subnets': []
        }

        for subnet in subnets:
            subnet_id = subnet['SubnetId']
            resources = get_resources_in_subnet(ec2_client, rds_client, elbv2_client, subnet_id)
            subnet_report = {
                'SubnetId': subnet_id,
                'CIDR': subnet['CidrBlock'],
                'AvailableIpAddressCount': subnet['AvailableIpAddressCount'],
                'Resources': resources
            }
            account_report['Subnets'].append(subnet_report)

        report_data.append(account_report)

    write_report(report_data)

if __name__ == "__main__":
    main()
