# AWS Subnet Report Generator

This script generates a comprehensive report of all subnets across multiple AWS accounts within an AWS Organization. It includes details about the CIDR blocks, available IPs, and resources (EC2 instances, RDS instances, and ELBv2 load balancers) using those subnets.

## Features

- Iterates over all accounts in an AWS Organization.
- Assumes a specified role in each account to gather subnet information.
- Collects details about EC2 instances, RDS instances, and ELBv2 load balancers in each subnet.
- Generates a CSV report with the collected data.

## Prerequisites

- Python 3.x
- Boto3 library
- AWS CLI configured with access to your AWS Organization's root account and the necessary permissions to assume roles in member accounts.


## Usage

1. **Modify the script**:
    - Ensure the role name (`YOUR_ROLE`) on line 111 is correct and the role exists in all member accounts.

2. **Run the script**:
    ```sh
    python script.py
    ```

3. **View the report**:
    - The script generates a CSV file named `subnets_report.csv` in the current directory.
    - Open the file to view the report.

## Error Handling

- The script includes error handling to continue processing other accounts even if some accounts have permission issues or other errors.
- Errors are logged to the console for review.

## Example Output

The generated `subnets_report.csv` includes the following columns:
- `AccountId`: The AWS account ID.
- `SubnetId`: The ID of the subnet.
- `CIDR`: The CIDR block of the subnet.
- `AvailableIPs`: The number of available IP addresses in the subnet.
- `ResourceType`: The type of resource using the subnet (EC2 instance, RDS instance, or ELBv2 load balancer).
- `ResourceId`: The ID of the resource.
- `ResourceDetails`: Additional details about the resource.

## Contributing

1. Clone the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## Acknowledgements

- [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) - The AWS SDK for Python.
