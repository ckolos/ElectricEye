# This file is part of ElectricEye.

# ElectricEye is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# ElectricEye is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with ElectricEye.  
# If not, see https://github.com/jonrau1/ElectricEye/blob/master/LICENSE.

import boto3
import os
import datetime
# import boto3 clients
sts = boto3.client('sts')
cloudformation = boto3.client('cloudformation')
securityhub = boto3.client('securityhub')
# create env vars for account and region
#awsRegion = os.environ['AWS_REGION']
awsRegion = 'us-east-1'
awsAccountId = sts.get_caller_identity()['Account']
# describe all cfn stacks
response = cloudformation.describe_stacks()
myCfnStacks = response['Stacks']

def cfn_drift_check():
    for stacks in myCfnStacks:
        stackName = str(stacks['StackName'])
        stackId = str(stacks['StackId'])
        stackArn = 'arn:aws:cloudformation:' + awsRegion + ':' + awsAccountId + ':stack/' + stackName + '/' + stackId
        driftCheck = str(stacks['DriftInformation']['StackDriftStatus'])
        if driftCheck != 'IN_SYNC':
            try:
                # ISO Time
                iso8601Time = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
                # create Sec Hub finding
                response = securityhub.batch_import_findings(
                    Findings=[
                        {
                            'SchemaVersion': '2018-10-08',
                            'Id': stackArn + '/cloudformation-drift-check',
                            'ProductArn': 'arn:aws:securityhub:' + awsRegion + ':' + awsAccountId + ':product/' + awsAccountId + '/default',
                            'GeneratorId': stackArn,
                            'AwsAccountId': awsAccountId,
                            'Types': [ 'Software and Configuration Checks/AWS Security Best Practices' ],
                            'FirstObservedAt': iso8601Time,
                            'CreatedAt': iso8601Time,
                            'UpdatedAt': iso8601Time,
                            'Severity': { 'Label': 'LOW' },
                            'Confidence': 99,
                            'Title': '[CloudFormation.1] CloudFormation stacks should be monitored for configuration drift',
                            'Description': 'CloudFormation stack ' + stackName + ' has not been monitored for drift detection. Refer to the remediation instructions if this configuration is not intended',
                            'Remediation': {
                                'Recommendation': {
                                    'Text': 'To learn more about drift detection refer to the Detecting Unmanaged Configuration Changes to Stacks and Resources section of the AWS CloudFormation User Guide',
                                    'Url': 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-stack-drift.html'
                                }
                            },
                            'ProductFields': {
                                'Product Name': 'ElectricEye'
                            },
                            'Resources': [
                                {
                                    'Type': 'AwsCloudFormationStack',
                                    'Id': stackArn,
                                    'Partition': 'aws',
                                    'Region': awsRegion,
                                    'Details': {
                                        'Other': { 'Stack Name': stackName }
                                    }
                                }
                            ],
                            'Compliance': { 'Status': 'FAILED' },
                            'RecordState': 'ACTIVE'
                        }
                    ]
                )
                print(response)
            except Exception as e:
                print(e)
        else:
            try:
                # ISO Time
                iso8601Time = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
                # create Sec Hub finding
                response = securityhub.batch_import_findings(
                    Findings=[
                        {
                            'SchemaVersion': '2018-10-08',
                            'Id': stackArn + '/cloudformation-drift-check',
                            'ProductArn': 'arn:aws:securityhub:' + awsRegion + ':' + awsAccountId + ':product/' + awsAccountId + '/default',
                            'GeneratorId': stackArn,
                            'AwsAccountId': awsAccountId,
                            'Types': [ 'Software and Configuration Checks/AWS Security Best Practices' ],
                            'FirstObservedAt': iso8601Time,
                            'CreatedAt': iso8601Time,
                            'UpdatedAt': iso8601Time,
                            'Severity': { 'Label': 'INFORMATIONAL' },
                            'Confidence': 99,
                            'Title': '[CloudFormation.1] CloudFormation stacks should be monitored for configuration drift',
                            'Description': 'CloudFormation stack ' + stackName + ' has been monitored for drift detection.',
                            'Remediation': {
                                'Recommendation': {
                                    'Text': 'To learn more about drift detection refer to the Detecting Unmanaged Configuration Changes to Stacks and Resources section of the AWS CloudFormation User Guide',
                                    'Url': 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-stack-drift.html'
                                }
                            },
                            'ProductFields': {
                                'Product Name': 'ElectricEye'
                            },
                            'Resources': [
                                {
                                    'Type': 'AwsCloudFormationStack',
                                    'Id': stackArn,
                                    'Partition': 'aws',
                                    'Region': awsRegion,
                                    'Details': {
                                        'Other': { 'Stack Name': stackName }
                                    }
                                }
                            ],
                            'Compliance': { 'Status': 'PASSED' },
                            'RecordState': 'ARCHIVED'
                        }
                    ]
                )
                print(response)
            except Exception as e:
                print(e)

def cfn_monitoring_check():
    for stacks in myCfnStacks:
        stackName = str(stacks['StackName'])
        stackId = str(stacks['StackId'])
        stackArn = 'arn:aws:cloudformation:' + awsRegion + ':' + awsAccountId + ':stack/' + stackName + '/' + stackId
        alertsCheck = str(stacks['NotificationARNs'])
        if alertsCheck == '[]':
            try:
                # ISO Time
                iso8601Time = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
                # create Sec Hub finding
                response = securityhub.batch_import_findings(
                    Findings=[
                        {
                            'SchemaVersion': '2018-10-08',
                            'Id': stackArn + '/cloudformation-monitoring-check',
                            'ProductArn': 'arn:aws:securityhub:' + awsRegion + ':' + awsAccountId + ':product/' + awsAccountId + '/default',
                            'GeneratorId': stackArn,
                            'AwsAccountId': awsAccountId,
                            'Types': [ 'Software and Configuration Checks/AWS Security Best Practices' ],
                            'FirstObservedAt': iso8601Time,
                            'CreatedAt': iso8601Time,
                            'UpdatedAt': iso8601Time,
                            'Severity': { 'Label': 'LOW' },
                            'Confidence': 99,
                            'Title': '[CloudFormation.2] CloudFormation stacks should be monitored for changes',
                            'Description': 'CloudFormation stack ' + stackName + ' does not have monitoring enabled. Refer to the remediation instructions if this configuration is not intended',
                            'Remediation': {
                                'Recommendation': {
                                    'Text': 'If your stack should having monitoring enabled refer to the Monitor and Roll Back Stack Operations section of the AWS CloudFormation User Guide',
                                    'Url': 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-rollback-triggers.html'
                                }
                            },
                            'ProductFields': {
                                'Product Name': 'ElectricEye'
                            },
                            'Resources': [
                                {
                                    'Type': 'AwsCloudFormationStack',
                                    'Id': stackArn,
                                    'Partition': 'aws',
                                    'Region': awsRegion,
                                    'Details': {
                                        'Other': { 'Stack Name': stackName }
                                    }
                                }
                            ],
                            'Compliance': { 'Status': 'FAILED' },
                            'RecordState': 'ACTIVE'
                        }
                    ]
                )
                print(response)
            except Exception as e:
                print(e)
        else:
            try:
                # ISO Time
                iso8601Time = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
                # create Sec Hub finding
                response = securityhub.batch_import_findings(
                    Findings=[
                        {
                            'SchemaVersion': '2018-10-08',
                            'Id': stackArn + '/cloudformation-monitoring-check',
                            'ProductArn': 'arn:aws:securityhub:' + awsRegion + ':' + awsAccountId + ':product/' + awsAccountId + '/default',
                            'GeneratorId': stackArn,
                            'AwsAccountId': awsAccountId,
                            'Types': [ 'Software and Configuration Checks/AWS Security Best Practices' ],
                            'FirstObservedAt': iso8601Time,
                            'CreatedAt': iso8601Time,
                            'UpdatedAt': iso8601Time,
                            'Severity': { 'Label': 'INFORMATIONAL' },
                            'Confidence': 99,
                            'Title': '[CloudFormation.2] CloudFormation stacks should be monitored for changes',
                            'Description': 'CloudFormation stack ' + stackName + ' has monitoring enabled.',
                            'Remediation': {
                                'Recommendation': {
                                    'Text': 'If your stack should having monitoring enabled refer to the Monitor and Roll Back Stack Operations section of the AWS CloudFormation User Guide',
                                    'Url': 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-rollback-triggers.html'
                                }
                            },
                            'ProductFields': {
                                'Product Name': 'ElectricEye'
                            },
                            'Resources': [
                                {
                                    'Type': 'AwsCloudFormationStack',
                                    'Id': stackArn,
                                    'Partition': 'aws',
                                    'Region': awsRegion,
                                    'Details': {
                                        'Other': { 'Stack Name': stackName }
                                    }
                                }
                            ],
                            'Compliance': { 'Status': 'PASSED' },
                            'RecordState': 'ARCHIVED'
                        }
                    ]
                )
                print(response)
            except Exception as e:
                print(e)
        
def cloudformation_auditor():
    cfn_drift_check()
    cfn_monitoring_check()

cloudformation_auditor()