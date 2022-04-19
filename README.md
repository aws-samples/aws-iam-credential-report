# Blog Post - [Automate IAM credential reports at scale across AWS](https://aws.amazon.com/blogs/infrastructure-and-automation/automate-iam-credential-reports-at-scale-across-aws/)

This solution demonstrates how to automate and consolidate AWS Identity and Access Management (IAM) credential reports for your AWS accounts using Infrastructure as code (IaC). With this solution, you can generate and download credential reports that lists all AWS IAM users in your accounts and the status of their various credentials, including passwords, access keys, and MFA devices. In this repository, you will find all the AWS CloudFormation templates and Python code that will build this solution in your AWS multi-environment. 


## Solution architecture and design
To assume a role across different AWS accounts that belong to AWS Organizations, the automation uses an AWS Lambda function in a management account. The Lambda function generates an IAM user credential report for each account, and it aggregates .csv reports in an S3 bucket deployed in a log-archive account. The S3 bucket in the log-archive account is encrypted with a customer managed AWS KMS key that’s located in a security account. 

## ![](/Images/IAMCredentialReport.png)


## Overview of the CloudFormation templates

1. [iam-credential-report-kms-key.yaml](./CloudFormation/iam-credential-report-kms-key.yaml) - This template creates the following resources in the central security account:

    - An AWS Key Management Service (KMS) customer-managed key that is used to encrypt an S3 bucket.
    - A KMS key alias.

2. [iam-credential-report-s3-bucket.yaml](./CloudFormation/iam-credential-report-s3-bucket.yaml) - This template creates a global Amazon Simple Storage Service (S3) bucket in the log archive account. The KMS key and S3 bucket must be deployed in the same region.


3. [iam-credential-report-automation.yaml](./CloudFormation/iam-credential-report-automation.yaml) - This template creates the following resources in the management account:

    - A global AWS Identity and Access Management (IAM) role and policy used as the invocation role for a regional lambda function. 
    - An AWS Lambda function that assumes a role in the member accounts to generate, fetch, and consolidate the IAM credential reports.
    - An Amazon CloudWatch log group that stores the log streams of the Lambda function.
    - An Amazon EventBridge rule that triggers the Lambda function using a schedule expression.


4. [iam-credential-report-iam-role.yaml](./CloudFormation/iam-credential-report-iam-role.yaml) - This template creates the following global resources in the member accounts:

    - An IAM role and policy to generate and obtain IAM credential report in a member account.
    - The IAM policy also allows the role to be assumed by the security account's Lambda invocation role.



## How to analyze IAM credential reports

The CSV reports created by this solution can be ingested by AWS services such as [Amazon Athena](https://aws.amazon.com/athena/?whats-new-cards.sort-by=item.additionalFields.postDateTime&whats-new-cards.sort-order=desc), [Amazon Quicksight](https://aws.amazon.com/quicksight/), or third-party products from our [AWS Partners](https://partners.amazonaws.com/search/partners?facets=Use%20Case%20%3A%20Data%20and%20Analytics%7CUse%20Case%20%3A%20Data%20and%20Analytics%20%3A%20BI%20and%20Visualization). For the purpose of this solution, I will focus on deploying the automation that will generate and store these IAM credential reports.


## Use cases

Your organization can use this solution in scenarios such as:

- A security engineer needs to provide evidence of IAM privilege access monitoring to an external auditor where detailed user metadata such as creation time, use of multi factor authentication, etc. can be attested to.
- A compliance manager needs to establish a process for user access review across a high-scale, multi-account AWS cloud infrastructure.
- A security manager needs to maintain an asset inventory for local IAM user accounts (such as service accounts), when their Passwords were last changed, if they have access keys and how often are these rotated.

## Additional deployment methods
Optionally, you can deploy this solution using an AWS CodePipeline in [Customizations for AWS Control Tower](https://aws.amazon.com/solutions/implementations/customizations-for-aws-control-tower/). You can also refactor the code and deploy the S3 bucket and AWS KMS key to a single AWS account. 

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.