import os
import boto3
import time
from botocore.exceptions import ClientError
from datetime import date

## Define Organization and STS Clients
orgClient = boto3.client('organizations')
stsClient = boto3.client('sts')

## Define current date
today = str(date.today())

## Read environment Variables from Lambda Function
BUCKET_ARN = os.environ['BUCKET_ARN']

## Setup bucket for storing reports
s3 = boto3.resource('s3')
bucketName = BUCKET_ARN.split(":", -1)[-1]
bucketConnection = s3.Bucket(bucketName)

paginator = orgClient.get_paginator('list_accounts')
page_iterator = paginator.paginate()

listedAccounts = []
for page in page_iterator:        
    for acct in page['Accounts']:
        listedAccounts.append(acct)

failedAccounts = []


def assumeRole(accountId):
    try:
        assumedRoleObject=stsClient.assume_role(
        RoleArn=f"arn:aws:iam::{accountId}:role/iam-credential-report",
        RoleSessionName="IAMCredentialReport")
        credentials=assumedRoleObject['Credentials']

        iamClient=boto3.client('iam',
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'])

        # Generate Credential Report
        reportcomplete = False
        while not reportcomplete:
           gencredentialreport = iamClient.generate_credential_report()
           print('IAM credential report successfully generated for account Id: ' + accountId)
           reportcomplete = gencredentialreport['State'] == 'COMPLETE'
           time.sleep (1)
        
        # Obtain credential report and send to S3
        if gencredentialreport['State'] == 'COMPLETE':
            credentialReport = iamClient.get_credential_report()
            decodedCredentialReport = credentialReport['Content'].decode("utf-8")
            ## Save credential Report into CSV file
            reportFileName = f"credentialReport_{accountId}.csv"
            with open("/tmp/"+reportFileName, "w") as file:
                file.write(decodedCredentialReport)
            s3.Object(bucketName, today+"/"+reportFileName).put(Body=open("/tmp/"+reportFileName, 'rb'),ACL='bucket-owner-full-control')
            return reportFileName
            
    except ClientError as error:
        failedAccounts.append(accountId)
        print(error)
        pass

def lambda_handler(event, context):
    for account in listedAccounts['Accounts']:
        if account['Status'] != 'SUSPENDED':
            assumeRole(account['Id'])
    return("Completed! Failed Accounts: ", failedAccounts)
