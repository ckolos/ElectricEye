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

resource "aws_vpc" "Electric_Eye_VPC" {
  cidr_block           = var.Electric_Eye_VPC_CIDR
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = {
      Name = var.Electric_Eye_VPC_Name_Tag
  }
}
resource "aws_subnet" "Electric_Eye_Public_Subnets" {
  count                   = var.Network_Resource_Count
  vpc_id                  = aws_vpc.Electric_Eye_VPC.id
  cidr_block              = cidrsubnet(aws_vpc.Electric_Eye_VPC.cidr_block, 8, var.Network_Resource_Count + count.index)
  availability_zone       = data.aws_availability_zones.Available_AZ.names[count.index]
  map_public_ip_on_launch = true
  tags = {
    Name = "${var.Electric_Eye_VPC_Name_Tag}-PUB-Subnet-${element(data.aws_availability_zones.Available_AZ.names, count.index)}"
  }
}
resource "aws_internet_gateway" "Electric_Eye_IGW" {
  vpc_id = aws_vpc.Electric_Eye_VPC.id
  tags = {
      Name = "${var.Electric_Eye_VPC_Name_Tag}-IGW"
  }
}
resource "aws_route_table" "Electric_Eye_Public_RTB" {
  count  = var.Network_Resource_Count
  vpc_id = aws_vpc.Electric_Eye_VPC.id
  route {
      cidr_block = "0.0.0.0/0"
      gateway_id = aws_internet_gateway.Electric_Eye_IGW.id
  }
  tags = {
    Name = "${var.Electric_Eye_VPC_Name_Tag}-PUB-RTB-${element(aws_subnet.Electric_Eye_Public_Subnets.*.id, count.index)}"
  }
}
resource "aws_vpc_endpoint" "Electric_Eye_Gateway_S3" {
  vpc_id            = aws_vpc.Electric_Eye_VPC.id
  service_name      = "com.amazonaws.${var.AWS_Region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = aws_route_table.Electric_Eye_Public_RTB[*].id
  tags = {
      Name = "${var.Electric_Eye_VPC_Name_Tag}-S3-Endpoint"
  }
}
resource "aws_vpc_endpoint" "Electric_Eye_Interface_Interface_ECR-DKR" {
  vpc_id              = aws_vpc.Electric_Eye_VPC.id
  service_name        = "com.amazonaws.${var.AWS_Region}.ecr.dkr"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.Electric_Eye_Public_Subnets[*].id
  security_group_ids  = [aws_security_group.Electric_Eye_Sec_Group.id]
  private_dns_enabled = true
  tags = {
      Name = "${var.Electric_Eye_VPC_Name_Tag}-ECR-DKR-Endpoint"
  }
}
resource "aws_route_table_association" "Public_Subnet_Association" {
  count          = var.Network_Resource_Count
  subnet_id      = element(aws_subnet.Electric_Eye_Public_Subnets.*.id, count.index)
  route_table_id = element(aws_route_table.Electric_Eye_Public_RTB.*.id, count.index)
}
resource "aws_flow_log" "Electric_Eye_VPC_Flow_Log" {
  iam_role_arn    = aws_iam_role.Electric_Eye_FlowLogs_to_CWL_Role.arn
  log_destination = aws_cloudwatch_log_group.Electric_Eye_FlowLogs_CWL_Group.arn
  traffic_type    = "ALL"
  vpc_id          = aws_vpc.Electric_Eye_VPC.id
}
resource "aws_cloudwatch_log_group" "Electric_Eye_FlowLogs_CWL_Group" {
  name = "FlowLogs/${var.Electric_Eye_VPC_Name_Tag}"
}
resource "aws_iam_role" "Electric_Eye_FlowLogs_to_CWL_Role" {
  name = "${var.Electric_Eye_VPC_Name_Tag}-flowlog-role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "vpc-flow-logs.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}
resource "aws_iam_role_policy" "Electric_Eye_FlowLogs_to_CWL_Role_Policy" {
  name = "${var.Electric_Eye_VPC_Name_Tag}-flowlog-role-policy"
  role = aws_iam_role.Electric_Eye_FlowLogs_to_CWL_Role.id
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:DescribeLogGroups",
        "logs:DescribeLogStreams"
      ],
      "Effect": "Allow",
      "Resource": "${aws_cloudwatch_log_group.Electric_Eye_FlowLogs_CWL_Group.arn}*"
    }
  ]
}
EOF
}
resource "aws_default_security_group" "Default_Security_Group" {
  vpc_id = aws_vpc.Electric_Eye_VPC.id
  tags = {
    Name = "DEFAULT_DO_NOT_USE"
  }
}
resource "aws_security_group" "Electric_Eye_Sec_Group" {
  name        = "${var.Electric_Eye_VPC_Name_Tag}-sec-group"
  description = "ElectricEye Security Group - Managed by Terraform"
  vpc_id      = aws_vpc.Electric_Eye_VPC.id
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    cidr_blocks     = ["0.0.0.0/0"]
  }
  tags = {
      Name = "${var.Electric_Eye_VPC_Name_Tag}-sec-group"
  }
}