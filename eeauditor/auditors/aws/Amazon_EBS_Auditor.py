#This file is part of ElectricEye.
#SPDX-License-Identifier: Apache-2.0

#Licensed to the Apache Software Foundation (ASF) under one
#or more contributor license agreements.  See the NOTICE file
#distributed with this work for additional information
#regarding copyright ownership.  The ASF licenses this file
#to you under the Apache License, Version 2.0 (the
#"License"); you may not use this file except in compliance
#with the License.  You may obtain a copy of the License at

#http://www.apache.org/licenses/LICENSE-2.0

#Unless required by applicable law or agreed to in writing,
#software distributed under the License is distributed on an
#"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#KIND, either express or implied.  See the License for the
#specific language governing permissions and limitations
#under the License.

import boto3
import datetime
from check_register import CheckRegister

registry = CheckRegister()

# import boto3 clients
ec2 = boto3.client("ec2")

# loop through EBS volumes
def describe_volumes(cache):
    response = cache.get("describe_volumes")
    if response:
        return response
    cache["describe_volumes"] = ec2.describe_volumes(DryRun=False, MaxResults=500)
    return cache["describe_volumes"]

# loop through EBS snapshots
def describe_snapshots(cache, awsAccountId):
    response = cache.get("describe_snapshots")
    if response:
        return response
    cache["describe_snapshots"] = ec2.describe_snapshots(OwnerIds=[awsAccountId], DryRun=False)
    return cache["describe_snapshots"]

@registry.register_check("ec2")
def ebs_volume_attachment_check(cache: dict, awsAccountId: str, awsRegion: str, awsPartition: str) -> dict:
    """[EBS.1] EBS Volumes should be in an attached state"""
    # ISO Time
    iso8601Time = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    for volumes in describe_volumes(cache)["Volumes"]:
        volumeId = str(volumes["VolumeId"])
        volumeArn = f"arn:{awsPartition}:ec2:{awsRegion}:{awsAccountId}:volume/{volumeId}"
        ebsAttachments = volumes["Attachments"]
        for attachments in ebsAttachments:
            ebsAttachmentState = str(attachments["State"])
            # this is a failing check
            if ebsAttachmentState != "attached":
                finding = {
                    "SchemaVersion": "2018-10-08",
                    "Id": f"{volumeArn}/ebs-volume-attachment-check",
                    "ProductArn": f"arn:{awsPartition}:securityhub:{awsRegion}:{awsAccountId}:product/{awsAccountId}/default",
                    "GeneratorId": volumeArn,
                    "AwsAccountId": awsAccountId,
                    "Types": ["Software and Configuration Checks/AWS Security Best Practices"],
                    "FirstObservedAt": iso8601Time,
                    "CreatedAt": iso8601Time,
                    "UpdatedAt": iso8601Time,
                    "Severity": {"Label": "LOW"},
                    "Confidence": 99,
                    "Title": "[EBS.1] EBS Volumes should be in an attached state",
                    "Description": "EBS Volume "
                    + volumeId
                    + " is not in an attached state. Refer to the remediation instructions if this configuration is not intended",
                    "Remediation": {
                        "Recommendation": {
                            "Text": "If your EBS volume should be attached refer to the Attaching an Amazon EBS Volume to an Instance section of the Amazon Elastic Compute Cloud User Guide",
                            "Url": "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-attaching-volume.html",
                        }
                    },
                    "ProductFields": {"Product Name": "ElectricEye"},
                    "Resources": [
                        {
                            "Type": "AwsEc2Volume",
                            "Id": volumeArn,
                            "Partition": awsPartition,
                            "Region": awsRegion
                        }
                    ],
                    "Compliance": {
                        "Status": "FAILED",
                        "RelatedRequirements": [
                            "NIST CSF ID.AM-2",
                            "NIST SP 800-53 CM-8",
                            "NIST SP 800-53 PM-5",
                            "AICPA TSC CC3.2",
                            "AICPA TSC CC6.1",
                            "ISO 27001:2013 A.8.1.1",
                            "ISO 27001:2013 A.8.1.2",
                            "ISO 27001:2013 A.12.5.1",
                        ],
                    },
                    "Workflow": {"Status": "NEW"},
                    "RecordState": "ACTIVE",
                }
                yield finding
            # this is a passing check
            else:
                finding = {
                    "SchemaVersion": "2018-10-08",
                    "Id": f"{volumeArn}/ebs-volume-attachment-check",
                    "ProductArn": f"arn:{awsPartition}:securityhub:{awsRegion}:{awsAccountId}:product/{awsAccountId}/default",
                    "GeneratorId": volumeArn,
                    "AwsAccountId": awsAccountId,
                    "Types": ["Software and Configuration Checks/AWS Security Best Practices"],
                    "FirstObservedAt": iso8601Time,
                    "CreatedAt": iso8601Time,
                    "UpdatedAt": iso8601Time,
                    "Severity": {"Label": "INFORMATIONAL"},
                    "Confidence": 99,
                    "Title": "[EBS.1] EBS Volumes should be in an attached state",
                    "Description": "EBS Volume " + volumeId + " is in an attached state.",
                    "Remediation": {
                        "Recommendation": {
                            "Text": "If your EBS volume should be attached refer to the Attaching an Amazon EBS Volume to an Instance section of the Amazon Elastic Compute Cloud User Guide",
                            "Url": "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-attaching-volume.html",
                        }
                    },
                    "ProductFields": {"Product Name": "ElectricEye"},
                    "Resources": [
                        {
                            "Type": "AwsEc2Volume",
                            "Id": volumeArn,
                            "Partition": awsPartition,
                            "Region": awsRegion
                        }
                    ],
                    "Compliance": {
                        "Status": "PASSED",
                        "RelatedRequirements": [
                            "NIST CSF ID.AM-2",
                            "NIST SP 800-53 CM-8",
                            "NIST SP 800-53 PM-5",
                            "AICPA TSC CC3.2",
                            "AICPA TSC CC6.1",
                            "ISO 27001:2013 A.8.1.1",
                            "ISO 27001:2013 A.8.1.2",
                            "ISO 27001:2013 A.12.5.1"
                        ]
                    },
                    "Workflow": {"Status": "RESOLVED"},
                    "RecordState": "ARCHIVED"
                }
                yield finding

@registry.register_check("ec2")
def ebs_volume_delete_on_termination_check(cache: dict, awsAccountId: str, awsRegion: str, awsPartition: str) -> dict:
    """[EBS.2] EBS Volumes should be configured to be deleted on termination"""
    # ISO Time
    iso8601Time = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    for volumes in describe_volumes(cache)["Volumes"]:
        volumeId = str(volumes["VolumeId"])
        volumeArn = f"arn:{awsPartition}:ec2:{awsRegion}:{awsAccountId}:volume/{volumeId}"
        ebsAttachments = volumes["Attachments"]
        for attachments in ebsAttachments:
            ebsDeleteOnTerminationCheck = str(attachments["DeleteOnTermination"])
            # this is a failing check
            if ebsDeleteOnTerminationCheck == "False":
                finding = {
                    "SchemaVersion": "2018-10-08",
                    "Id": f"{volumeArn}/ebs-volume-delete-on-termination-check",
                    "ProductArn": f"arn:{awsPartition}:securityhub:{awsRegion}:{awsAccountId}:product/{awsAccountId}/default",
                    "GeneratorId": volumeArn,
                    "AwsAccountId": awsAccountId,
                    "Types": ["Software and Configuration Checks/AWS Security Best Practices"],
                    "FirstObservedAt": iso8601Time,
                    "CreatedAt": iso8601Time,
                    "UpdatedAt": iso8601Time,
                    "Severity": {"Label": "LOW"},
                    "Confidence": 99,
                    "Title": "[EBS.2] EBS Volumes should be configured to be deleted on termination",
                    "Description": "EBS Volume "
                    + volumeId
                    + " is not configured to be deleted on termination. Refer to the remediation instructions if this configuration is not intended",
                    "Remediation": {
                        "Recommendation": {
                            "Text": "If your EBS volume should be deleted on instance termination refer to the Preserving Amazon EBS Volumes on Instance Termination section of the Amazon Elastic Compute Cloud User Guide",
                            "Url": "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/terminating-instances.html#preserving-volumes-on-termination",
                        }
                    },
                    "ProductFields": {"Product Name": "ElectricEye"},
                    "Resources": [
                        {
                            "Type": "AwsEc2Volume",
                            "Id": volumeArn,
                            "Partition": awsPartition,
                            "Region": awsRegion
                        }
                    ],
                    "Compliance": {
                        "Status": "FAILED",
                        "RelatedRequirements": [
                            "NIST CSF ID.AM-2",
                            "NIST SP 800-53 CM-8",
                            "NIST SP 800-53 PM-5",
                            "AICPA TSC CC3.2",
                            "AICPA TSC CC6.1",
                            "ISO 27001:2013 A.8.1.1",
                            "ISO 27001:2013 A.8.1.2",
                            "ISO 27001:2013 A.12.5.1",
                        ],
                    },
                    "Workflow": {"Status": "NEW"},
                    "RecordState": "ACTIVE",
                }
                yield finding
            # this is a passing check
            else:
                finding = {
                    "SchemaVersion": "2018-10-08",
                    "Id": f"{volumeArn}/ebs-volume-delete-on-termination-check",
                    "ProductArn": f"arn:{awsPartition}:securityhub:{awsRegion}:{awsAccountId}:product/{awsAccountId}/default",
                    "GeneratorId": volumeArn,
                    "AwsAccountId": awsAccountId,
                    "Types": ["Software and Configuration Checks/AWS Security Best Practices"],
                    "FirstObservedAt": iso8601Time,
                    "CreatedAt": iso8601Time,
                    "UpdatedAt": iso8601Time,
                    "Severity": {"Label": "INFORMATIONAL"},
                    "Confidence": 99,
                    "Title": "[EBS.2] EBS Volumes should be configured to be deleted on termination",
                    "Description": "EBS Volume "
                    + volumeId
                    + " is configured to be deleted on termination.",
                    "Remediation": {
                        "Recommendation": {
                            "Text": "If your EBS volume should be deleted on instance termination refer to the Preserving Amazon EBS Volumes on Instance Termination section of the Amazon Elastic Compute Cloud User Guide",
                            "Url": "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/terminating-instances.html#preserving-volumes-on-termination",
                        }
                    },
                    "ProductFields": {"Product Name": "ElectricEye"},
                    "Resources": [
                        {
                            "Type": "AwsEc2Volume",
                            "Id": volumeArn,
                            "Partition": awsPartition,
                            "Region": awsRegion
                        }
                    ],
                    "Compliance": {
                        "Status": "PASSED",
                        "RelatedRequirements": [
                            "NIST CSF ID.AM-2",
                            "NIST SP 800-53 CM-8",
                            "NIST SP 800-53 PM-5",
                            "AICPA TSC CC3.2",
                            "AICPA TSC CC6.1",
                            "ISO 27001:2013 A.8.1.1",
                            "ISO 27001:2013 A.8.1.2",
                            "ISO 27001:2013 A.12.5.1",
                        ],
                    },
                    "Workflow": {"Status": "RESOLVED"},
                    "RecordState": "ARCHIVED",
                }
                yield finding

@registry.register_check("ec2")
def ebs_volume_encryption_check(cache: dict, awsAccountId: str, awsRegion: str, awsPartition: str) -> dict:
    """[EBS.3] EBS Volumes should be encrypted"""
    # ISO Time
    iso8601Time = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    for volumes in describe_volumes(cache)["Volumes"]:
        volumeId = str(volumes["VolumeId"])
        volumeArn = f"arn:{awsPartition}:ec2:{awsRegion}:{awsAccountId}:volume/{volumeId}"
        ebsEncryptionCheck = volumes["Encrypted"]
        # this is a failing check
        if ebsEncryptionCheck == False:
            finding = {
                "SchemaVersion": "2018-10-08",
                "Id": f"{volumeArn}/ebs-volume-encryption-check",
                "ProductArn": f"arn:{awsPartition}:securityhub:{awsRegion}:{awsAccountId}:product/{awsAccountId}/default",
                "GeneratorId": volumeArn,
                "AwsAccountId": awsAccountId,
                "Types": [
                    "Software and Configuration Checks/AWS Security Best Practices",
                    "Effects/Data Exposure"
                ],
                "FirstObservedAt": iso8601Time,
                "CreatedAt": iso8601Time,
                "UpdatedAt": iso8601Time,
                "Severity": {"Label": "HIGH"},
                "Confidence": 99,
                "Title": "[EBS.3] EBS Volumes should be encrypted",
                "Description": "EBS Volume "
                + volumeId
                + " is not encrypted. Refer to the remediation instructions if this configuration is not intended",
                "Remediation": {
                    "Recommendation": {
                        "Text": "If your EBS volume should be encrypted refer to the Amazon EBS Encryption section of the Amazon Elastic Compute Cloud User Guide",
                        "Url": "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSEncryption.html",
                    }
                },
                "ProductFields": {"Product Name": "ElectricEye"},
                "Resources": [
                    {
                        "Type": "AwsEc2Volume",
                        "Id": volumeArn,
                        "Partition": awsPartition,
                        "Region": awsRegion,
                        "Details": {
                            "AwsEc2Volume": {
                                "Encrypted": False
                            }
                        }
                    }
                ],
                "Compliance": {
                    "Status": "FAILED",
                    "RelatedRequirements": [
                        "NIST CSF PR.DS-1",
                        "NIST SP 800-53 MP-8",
                        "NIST SP 800-53 SC-12",
                        "NIST SP 800-53 SC-28",
                        "AICPA TSC CC6.1",
                        "ISO 27001:2013 A.8.2.3"
                    ]
                },
                "Workflow": {"Status": "NEW"},
                "RecordState": "ACTIVE"
            }
            yield finding
        # this is a passing check
        else:
            finding = {
                "SchemaVersion": "2018-10-08",
                "Id": f"{volumeArn}/ebs-volume-encryption-check",
                "ProductArn": f"arn:{awsPartition}:securityhub:{awsRegion}:{awsAccountId}:product/{awsAccountId}/default",
                "GeneratorId": volumeArn,
                "AwsAccountId": awsAccountId,
                "Types": [
                    "Software and Configuration Checks/AWS Security Best Practices",
                    "Effects/Data Exposure"
                ],
                "FirstObservedAt": iso8601Time,
                "CreatedAt": iso8601Time,
                "UpdatedAt": iso8601Time,
                "Severity": {"Label": "INFORMATIONAL"},
                "Confidence": 99,
                "Title": "[EBS.3] EBS Volumes should be encrypted",
                "Description": f"EBS Volume {volumeId} is encrypted.",
                "Remediation": {
                    "Recommendation": {
                        "Text": "If your EBS volume should be encrypted refer to the Amazon EBS Encryption section of the Amazon Elastic Compute Cloud User Guide",
                        "Url": "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSEncryption.html",
                    }
                },
                "ProductFields": {"Product Name": "ElectricEye"},
                "Resources": [
                    {
                        "Type": "AwsEc2Volume",
                        "Id": volumeArn,
                        "Partition": awsPartition,
                        "Region": awsRegion,
                        "Details": {
                            "AwsEc2Volume": {
                                "Encrypted": True
                            }
                        }
                    }
                ],
                "Compliance": {
                    "Status": "PASSED",
                    "RelatedRequirements": [
                        "NIST CSF PR.DS-1",
                        "NIST SP 800-53 MP-8",
                        "NIST SP 800-53 SC-12",
                        "NIST SP 800-53 SC-28",
                        "AICPA TSC CC6.1",
                        "ISO 27001:2013 A.8.2.3",
                    ],
                },
                "Workflow": {"Status": "RESOLVED"},
                "RecordState": "ARCHIVED",
            }
            yield finding

@registry.register_check("ec2")
def ebs_snapshot_encryption_check(cache: dict, awsAccountId: str, awsRegion: str, awsPartition: str) -> dict:
    """[EBS.4] EBS Snapshots should be encrypted"""
    # ISO Time
    iso8601Time = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    for snapshots in describe_snapshots(cache, awsAccountId)["Snapshots"]:
        snapshotId = str(snapshots["SnapshotId"])
        snapshotArn = f"arn:{awsPartition}:ec2:{awsRegion}::snapshot/{snapshotId}"
        snapshotEncryptionCheck = snapshots["Encrypted"]
        # this is a failing check
        if snapshotEncryptionCheck == False:
            finding = {
                "SchemaVersion": "2018-10-08",
                "Id": f"{snapshotArn}/ebs-snapshot-encryption-check",
                "ProductArn": f"arn:{awsPartition}:securityhub:{awsRegion}:{awsAccountId}:product/{awsAccountId}/default",
                "GeneratorId": snapshotArn,
                "AwsAccountId": awsAccountId,
                "Types": [
                    "Software and Configuration Checks/AWS Security Best Practices",
                    "Effects/Data Exposure",
                ],
                "FirstObservedAt": iso8601Time,
                "CreatedAt": iso8601Time,
                "UpdatedAt": iso8601Time,
                "Severity": {"Label": "HIGH"},
                "Confidence": 99,
                "Title": "[EBS.4] EBS Snapshots should be encrypted",
                "Description": "EBS Snapshot "
                + snapshotId
                + " is not encrypted. Refer to the remediation instructions if this configuration is not intended",
                "Remediation": {
                    "Recommendation": {
                        "Text": "If your EBS snapshot should be encrypted refer to the Encryption Support for Snapshots section of the Amazon Elastic Compute Cloud User Guide",
                        "Url": "https://docs.aws.amazon.com/AWSEC2/latest/WindowsGuide/EBSSnapshots.html#encryption-support",
                    }
                },
                "ProductFields": {"Product Name": "ElectricEye"},
                "Resources": [
                    {
                        "Type": "AwsEc2Snapshot",
                        "Id": snapshotArn,
                        "Partition": awsPartition,
                        "Region": awsRegion,
                        "Details": {
                            "AwsEc2Volume": {
                                "Encrypted": False,
                                "SnapshotId": snapshotId
                            }
                        }
                    }
                ],
                "Compliance": {
                    "Status": "FAILED",
                    "RelatedRequirements": [
                        "NIST CSF PR.DS-1",
                        "NIST SP 800-53 MP-8",
                        "NIST SP 800-53 SC-12",
                        "NIST SP 800-53 SC-28",
                        "AICPA TSC CC6.1",
                        "ISO 27001:2013 A.8.2.3"
                    ]
                },
                "Workflow": {"Status": "NEW"},
                "RecordState": "ACTIVE"
            }
            yield finding
        # this is a passing check
        else:
            finding = {
                "SchemaVersion": "2018-10-08",
                "Id": f"{snapshotArn}/ebs-snapshot-encryption-check",
                "ProductArn": f"arn:{awsPartition}:securityhub:{awsRegion}:{awsAccountId}:product/{awsAccountId}/default",
                "GeneratorId": snapshotArn,
                "AwsAccountId": awsAccountId,
                "Types": [
                    "Software and Configuration Checks/AWS Security Best Practices",
                    "Effects/Data Exposure",
                ],
                "FirstObservedAt": iso8601Time,
                "CreatedAt": iso8601Time,
                "UpdatedAt": iso8601Time,
                "Severity": {"Label": "INFORMATIONAL"},
                "Confidence": 99,
                "Title": "[EBS.4] EBS Snapshots should be encrypted",
                "Description": f"EBS Snapshot {snapshotId} is encrypted.",
                "Remediation": {
                    "Recommendation": {
                        "Text": "If your EBS snapshot should be encrypted refer to the Encryption Support for Snapshots section of the Amazon Elastic Compute Cloud User Guide",
                        "Url": "https://docs.aws.amazon.com/AWSEC2/latest/WindowsGuide/EBSSnapshots.html#encryption-support",
                    }
                },
                "ProductFields": {"Product Name": "ElectricEye"},
                "Resources": [
                    {
                        "Type": "AwsEc2Snapshot",
                        "Id": snapshotArn,
                        "Partition": awsPartition,
                        "Region": awsRegion,
                        "Details": {
                            "AwsEc2Volume": {
                                "Encrypted": True,
                                "SnapshotId": snapshotId
                            }
                        }
                    }
                ],
                "Compliance": {
                    "Status": "PASSED",
                    "RelatedRequirements": [
                        "NIST CSF PR.DS-1",
                        "NIST SP 800-53 MP-8",
                        "NIST SP 800-53 SC-12",
                        "NIST SP 800-53 SC-28",
                        "AICPA TSC CC6.1",
                        "ISO 27001:2013 A.8.2.3"
                    ]
                },
                "Workflow": {"Status": "RESOLVED"},
                "RecordState": "ARCHIVED"
            }
            yield finding

@registry.register_check("ec2")
def ebs_snapshot_public_check(cache: dict, awsAccountId: str, awsRegion: str, awsPartition: str) -> dict:
    """[EBS.5] EBS Snapshots should not be public"""
    # ISO Time
    iso8601Time = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    for snapshots in describe_snapshots(cache, awsAccountId)["Snapshots"]:
        snapshotId = str(snapshots["SnapshotId"])
        snapshotArn = f"arn:{awsPartition}:ec2:{awsRegion}::snapshot/{snapshotId}"
        # determine if there are any permissions to share the snapshot
        r = ec2.describe_snapshot_attribute(
            Attribute="createVolumePermission",
            SnapshotId=snapshotId,
            DryRun=False
        )
        # this is a passing check
        if not r["CreateVolumePermissions"]:
            finding = {
                "SchemaVersion": "2018-10-08",
                "Id": f"{snapshotArn}/ebs-snapshot-public-share-check",
                "ProductArn": f"arn:{awsPartition}:securityhub:{awsRegion}:{awsAccountId}:product/{awsAccountId}/default",
                "GeneratorId": snapshotArn,
                "AwsAccountId": awsAccountId,
                "Types": [
                    "Software and Configuration Checks/AWS Security Best Practices",
                    "Effects/Data Exposure"
                ],
                "FirstObservedAt": iso8601Time,
                "CreatedAt": iso8601Time,
                "UpdatedAt": iso8601Time,
                "Severity": {"Label": "INFORMATIONAL"},
                "Confidence": 99,
                "Title": "[EBS.5] EBS Snapshots should not be public",
                "Description": f"EBS Snapshot {snapshotId} is private.",
                "Remediation": {
                    "Recommendation": {
                        "Text": "If your EBS snapshot should not be public refer to the Sharing an Amazon EBS Snapshot section of the Amazon Elastic Compute Cloud User Guide",
                        "Url": "https://docs.aws.amazon.com/AWSEC2/latest/WindowsGuide/ebs-modifying-snapshot-permissions.html"
                    }
                },
                "ProductFields": {"Product Name": "ElectricEye"},
                "Resources": [
                    {
                        "Type": "AwsEc2Snapshot",
                        "Id": snapshotArn,
                        "Partition": awsPartition,
                        "Region": awsRegion,
                        "Details": {
                            "AwsEc2Volume": {
                                "SnapshotId": snapshotId
                            }
                        }
                    }
                ],
                "Compliance": {
                    "Status": "PASSED",
                    "RelatedRequirements": [
                        "NIST CSF PR.AC-3",
                        "NIST SP 800-53 AC-1",
                        "NIST SP 800-53 AC-17",
                        "NIST SP 800-53 AC-19",
                        "NIST SP 800-53 AC-20",
                        "NIST SP 800-53 SC-15",
                        "AICPA TSC CC6.6",
                        "ISO 27001:2013 A.6.2.1",
                        "ISO 27001:2013 A.6.2.2",
                        "ISO 27001:2013 A.11.2.6",
                        "ISO 27001:2013 A.13.1.1",
                        "ISO 27001:2013 A.13.2.1"
                    ]
                },
                "Workflow": {"Status": "RESOLVED"},
                "RecordState": "ARCHIVED"
            }
            yield finding
        else:
            for permissions in r["CreateVolumePermissions"]:
                # {'Group': 'all'} denotes public
                # you should still audit accounts you have shared
                # this is a failing check
                if str(permissions) == "{'Group': 'all'}":
                    finding = {
                        "SchemaVersion": "2018-10-08",
                        "Id": f"{snapshotArn}/ebs-snapshot-public-share-check",
                        "ProductArn": f"arn:{awsPartition}:securityhub:{awsRegion}:{awsAccountId}:product/{awsAccountId}/default",
                        "GeneratorId": snapshotArn,
                        "AwsAccountId": awsAccountId,
                        "Types": [
                            "Software and Configuration Checks/AWS Security Best Practices",
                            "Effects/Data Exposure"
                        ],
                        "FirstObservedAt": iso8601Time,
                        "CreatedAt": iso8601Time,
                        "UpdatedAt": iso8601Time,
                        "Severity": {"Label": "CRITICAL"},
                        "Confidence": 99,
                        "Title": "[EBS.5] EBS Snapshots should not be public",
                        "Description": f"EBS Snapshot {snapshotId} is public. Snapshots that are public are restorable into Volumes or Amazon Machine Images (AMIs) by anyone with an AWS Account, if sensitive data is contained on the snapshot then adversaries can easily harvest it. Ensure you carefully examine the data stored onto root volumes as well as their permissions. Refer to the remediation instructions to remediate this behavior.",
                        "Remediation": {
                            "Recommendation": {
                                "Text": "If your EBS snapshot should not be public refer to the Sharing an Amazon EBS Snapshot section of the Amazon Elastic Compute Cloud User Guide",
                                "Url": "https://docs.aws.amazon.com/AWSEC2/latest/WindowsGuide/ebs-modifying-snapshot-permissions.html"
                            }
                        },
                        "ProductFields": {"Product Name": "ElectricEye"},
                        "Resources": [
                            {
                                "Type": "AwsEc2Snapshot",
                                "Id": snapshotArn,
                                "Partition": awsPartition,
                                "Region": awsRegion,
                                "Details": {
                                    "AwsEc2Volume": {
                                        "SnapshotId": snapshotId
                                    }
                                }
                            }
                        ],
                        "Compliance": {
                            "Status": "FAILED",
                            "RelatedRequirements": [
                                "NIST CSF PR.AC-3",
                                "NIST SP 800-53 AC-1",
                                "NIST SP 800-53 AC-17",
                                "NIST SP 800-53 AC-19",
                                "NIST SP 800-53 AC-20",
                                "NIST SP 800-53 SC-15",
                                "AICPA TSC CC6.6",
                                "ISO 27001:2013 A.6.2.1",
                                "ISO 27001:2013 A.6.2.2",
                                "ISO 27001:2013 A.11.2.6",
                                "ISO 27001:2013 A.13.1.1",
                                "ISO 27001:2013 A.13.2.1"
                            ]
                        },
                        "Workflow": {"Status": "NEW"},
                        "RecordState": "ACTIVE"
                    }
                    yield finding
                else:
                    # this is an active check, but not failing
                    finding = {
                        "SchemaVersion": "2018-10-08",
                        "Id": f"{snapshotArn}/ebs-snapshot-public-share-check",
                        "ProductArn": f"arn:{awsPartition}:securityhub:{awsRegion}:{awsAccountId}:product/{awsAccountId}/default",
                        "GeneratorId": snapshotArn,
                        "AwsAccountId": awsAccountId,
                        "Types": [
                            "Software and Configuration Checks/AWS Security Best Practices",
                            "Effects/Data Exposure"
                        ],
                        "FirstObservedAt": iso8601Time,
                        "CreatedAt": iso8601Time,
                        "UpdatedAt": iso8601Time,
                        "Severity": {"Label": "INFORMATIONAL"},
                        "Confidence": 99,
                        "Title": "[EBS.5] EBS Snapshots should not be public",
                        "Description": f"EBS Snapshot {snapshotId} is private, however, this snapshot has been identified as being shared with other accounts. You should audit these accounts to ensure they are still authorized to have this snapshot shared with them.",
                        "Remediation": {
                            "Recommendation": {
                                "Text": "If your EBS snapshot should not be public refer to the Sharing an Amazon EBS Snapshot section of the Amazon Elastic Compute Cloud User Guide",
                                "Url": "https://docs.aws.amazon.com/AWSEC2/latest/WindowsGuide/ebs-modifying-snapshot-permissions.html"
                            }
                        },
                        "ProductFields": {"Product Name": "ElectricEye"},
                        "Resources": [
                            {
                                "Type": "AwsEc2Snapshot",
                                "Id": snapshotArn,
                                "Partition": awsPartition,
                                "Region": awsRegion,
                                "Details": {
                                    "AwsEc2Volume": {
                                        "SnapshotId": snapshotId
                                    }
                                }
                            }
                        ],
                        "Compliance": {
                            "Status": "PASSED",
                            "RelatedRequirements": [
                                "NIST CSF PR.AC-3",
                                "NIST SP 800-53 AC-1",
                                "NIST SP 800-53 AC-17",
                                "NIST SP 800-53 AC-19",
                                "NIST SP 800-53 AC-20",
                                "NIST SP 800-53 SC-15",
                                "AICPA TSC CC6.6",
                                "ISO 27001:2013 A.6.2.1",
                                "ISO 27001:2013 A.6.2.2",
                                "ISO 27001:2013 A.11.2.6",
                                "ISO 27001:2013 A.13.1.1",
                                "ISO 27001:2013 A.13.2.1"
                            ]
                        },
                        "Workflow": {"Status": "NEW"},
                        "RecordState": "ACTIVE"
                    }
                    yield finding
                # break the loop since we already evaluated
                break

@registry.register_check("ec2")
def ebs_account_encryption_by_default_check(cache: dict, awsAccountId: str, awsRegion: str, awsPartition: str) -> dict:
    """[EBS.6] Account-level EBS Volume encryption should be enabled"""
    # ISO Time
    iso8601Time = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    # this is a failing check
    if ec2.get_ebs_encryption_by_default(DryRun=False)["EbsEncryptionByDefault"] == False:
        finding = {
            "SchemaVersion": "2018-10-08",
            "Id": f"{awsAccountId}{awsRegion}/ebs-account-encryption-check",
            "ProductArn": f"arn:{awsPartition}:securityhub:{awsRegion}:{awsAccountId}:product/{awsAccountId}/default",
            "GeneratorId": f"{awsAccountId}{awsRegion}",
            "AwsAccountId": awsAccountId,
            "Types": ["Software and Configuration Checks/AWS Security Best Practices"],
            "FirstObservedAt": iso8601Time,
            "CreatedAt": iso8601Time,
            "UpdatedAt": iso8601Time,
            "Severity": {"Label": "MEDIUM"},
            "Confidence": 99,
            "Title": "[EBS.6] Account-level EBS Volume encryption should be enabled",
            "Description": f"Account-level EBS volume encryption is not enabled for AWS Account {awsAccountId} in {awsRegion}. Refer to the remediation instructions if this configuration is not intended.",
            "Remediation": {
                "Recommendation": {
                    "Text": "For information on Account-level encryption refer to the Encryption by Default to an Instance section of the Amazon Elastic Compute Cloud User Guide",
                    "Url": "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSEncryption.html#encryption-by-default"
                }
            },
            "ProductFields": {"Product Name": "ElectricEye"},
            "Resources": [
                {
                    "Type": "AwsAccount",
                    "Id": f"{awsPartition.upper()}::::Account:{awsAccountId}",
                    "Partition": awsPartition,
                    "Region": awsRegion
                }
            ],
            "Compliance": {
                "Status": "FAILED",
                "RelatedRequirements": [
                    "NIST CSF PR.DS-1",
                    "NIST SP 800-53 MP-8",
                    "NIST SP 800-53 SC-12",
                    "NIST SP 800-53 SC-28",
                    "AICPA TSC CC6.1",
                    "ISO 27001:2013 A.8.2.3"
                ]
            },
            "Workflow": {"Status": "NEW"},
            "RecordState": "ACTIVE"
        }
        yield finding
    # this is a passing check
    else:
        finding = {
            "SchemaVersion": "2018-10-08",
            "Id": f"{awsAccountId}{awsRegion}/ebs-account-encryption-check",
            "ProductArn": f"arn:{awsPartition}:securityhub:{awsRegion}:{awsAccountId}:product/{awsAccountId}/default",
            "GeneratorId": f"{awsAccountId}{awsRegion}",
            "AwsAccountId": awsAccountId,
            "Types": ["Software and Configuration Checks/AWS Security Best Practices"],
            "FirstObservedAt": iso8601Time,
            "CreatedAt": iso8601Time,
            "UpdatedAt": iso8601Time,
            "Severity": {"Label": "INFORMATIONAL"},
            "Confidence": 99,
            "Title": "[EBS.6] Account-level EBS Volume encryption should be enabled",
            "Description": "Account-level EBS volume encryption is enabled for AWS Account {awsAccountId} in {awsRegion}.",
            "Remediation": {
                "Recommendation": {
                    "Text": "For information on Account-level encryption refer to the Encryption by Default to an Instance section of the Amazon Elastic Compute Cloud User Guide",
                    "Url": "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSEncryption.html#encryption-by-default"
                }
            },
            "ProductFields": {"Product Name": "ElectricEye"},
            "Resources": [
                {
                    "Type": "AwsAccount",
                    "Id": f"{awsPartition.upper()}::::Account:{awsAccountId}",
                    "Partition": awsPartition,
                    "Region": awsRegion
                }
            ],
            "Compliance": {
                "Status": "PASSED",
                "RelatedRequirements": [
                    "NIST CSF PR.DS-1",
                    "NIST SP 800-53 MP-8",
                    "NIST SP 800-53 SC-12",
                    "NIST SP 800-53 SC-28",
                    "AICPA TSC CC6.1",
                    "ISO 27001:2013 A.8.2.3"
                ]
            },
            "Workflow": {"Status": "RESOLVED"},
            "RecordState": "ARCHIVED"
        }
        yield finding

@registry.register_check("ec2")
def ebs_volume_snapshot_check(cache: dict, awsAccountId: str, awsRegion: str, awsPartition: str) -> dict:
    """[EBS.7] EBS Volumes should have snapshots"""
    # ISO Time
    iso8601Time = (datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat())
    for volumes in describe_volumes(cache)["Volumes"]:
        volumeId = str(volumes["VolumeId"])
        volumeArn = f"arn:{awsPartition}:ec2:{awsRegion}:{awsAccountId}:volume/{volumeId}"
        # Check if there is a volume
        try:
            snapshotId = str(volumes["SnapshotId"])
        except KeyError:
            snapshotId = None
        # This is a passing finding        
        if snapshotId != None:
            finding = {
                "SchemaVersion": "2018-10-08",
                "Id": f"{volumeArn}/ebs-volume-snapshot-check",
                "ProductArn": f"arn:{awsPartition}:securityhub:{awsRegion}:{awsAccountId}:product/{awsAccountId}/default",
                "GeneratorId": f"{volumeArn}/{snapshotId}",
                "AwsAccountId": awsAccountId,
                "Types": ["Software and Configuration Checks/AWS Security Best Practices"],
                "FirstObservedAt": iso8601Time,
                "CreatedAt": iso8601Time,
                "UpdatedAt": iso8601Time,
                "Severity": {"Label": "INFORMATIONAL"},
                "Confidence": 99,
                "Title": "[EBS.7] EBS Volumes should have snapshots",
                "Description": "EBS Volume "
                + volumeId
                + " has a snapshot which can promote cyber resilience due to a viable backup.",
                "Remediation": {
                    "Recommendation": {
                        "Text": "If your EBS volume should be backed up via Snapshots refer to the Amazon EBS snapshots section of the Amazon Elastic Compute Cloud User Guide",
                        "Url": "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSSnapshots.html",
                    }
                },
                "ProductFields": {"Product Name": "ElectricEye"},
                "Resources": [
                    {
                        "Type": "AwsEc2Volume",
                        "Id": volumeArn,
                        "Partition": awsPartition,
                        "Region": awsRegion,
                        "Details": {
                            "AwsEc2Volume": {
                                "SnapshotId": snapshotId
                            }
                        }
                    }
                ],
                "Compliance": {
                    "Status": "PASSED",
                    "RelatedRequirements": [
                        "NIST CSF ID.BE-5",
                        "NIST CSF PR.PT-5",
                        "NIST SP 800-53 CP-2",
                        "NIST SP 800-53 CP-11",
                        "NIST SP 800-53 SA-13",
                        "NIST SP 800-53 SA14",
                        "AICPA TSC CC3.1",
                        "AICPA TSC A1.2",
                        "ISO 27001:2013 A.11.1.4",
                        "ISO 27001:2013 A.17.1.1",
                        "ISO 27001:2013 A.17.1.2",
                        "ISO 27001:2013 A.17.2.1"
                    ]
                },
                "Workflow": {"Status": "RESOLVED"},
                "RecordState": "ARCHIVED"
            }
            yield finding
        else:
            finding = {
                "SchemaVersion": "2018-10-08",
                "Id": f"{volumeArn}/ebs-volume-snapshot-check",
                "ProductArn": f"arn:{awsPartition}:securityhub:{awsRegion}:{awsAccountId}:product/{awsAccountId}/default",
                "GeneratorId": f"{volumeArn}/{snapshotId}",
                "AwsAccountId": awsAccountId,
                "Types": ["Software and Configuration Checks/AWS Security Best Practices"],
                "FirstObservedAt": iso8601Time,
                "CreatedAt": iso8601Time,
                "UpdatedAt": iso8601Time,
                "Severity": {"Label": "LOW"},
                "Confidence": 99,
                "Title": "[EBS.7] EBS Volumes should have snapshots",
                "Description": "EBS Volume "
                + volumeId
                + " does not have a snapshot which can reduce cyber resilience due to a lack of a viable backup. Refer to the remediation instructions if this configuration is not intended",
                "Remediation": {
                    "Recommendation": {
                        "Text": "If your EBS volume should be backed up via Snapshots refer to the Amazon EBS snapshots section of the Amazon Elastic Compute Cloud User Guide",
                        "Url": "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSSnapshots.html",
                    }
                },
                "ProductFields": {"Product Name": "ElectricEye"},
                "Resources": [
                    {
                        "Type": "AwsEc2Volume",
                        "Id": volumeArn,
                        "Partition": awsPartition,
                        "Region": awsRegion,
                        "Details": {
                            "AwsEc2Volume": {
                                "SnapshotId": snapshotId
                            }
                        }
                    }
                ],
                "Compliance": {
                    "Status": "FAILED",
                    "RelatedRequirements": [
                        "NIST CSF ID.BE-5",
                        "NIST CSF PR.PT-5",
                        "NIST SP 800-53 CP-2",
                        "NIST SP 800-53 CP-11",
                        "NIST SP 800-53 SA-13",
                        "NIST SP 800-53 SA14",
                        "AICPA TSC CC3.1",
                        "AICPA TSC A1.2",
                        "ISO 27001:2013 A.11.1.4",
                        "ISO 27001:2013 A.17.1.1",
                        "ISO 27001:2013 A.17.1.2",
                        "ISO 27001:2013 A.17.2.1"
                    ]
                },
                "Workflow": {"Status": "NEW"},
                "RecordState": "ACTIVE"
            }
            yield finding