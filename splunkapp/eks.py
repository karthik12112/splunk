from vpc.vpc import create_vpc
from subnets.subnets import create_subnet
from iam.iam_eks import (create_prod_template)
from troposphere import Parameter, Ref, Template
from security_groups.eks_sg import create_sg
import troposphere.ec2 as ec2
from troposphere import (
    Template,
    Select,
    GetAZs,
    GetAtt,
    Tags,
    Sub
)
from troposphere.iam import (
    Role,
    PolicyType,
    InstanceProfile
)
from troposphere.policies import (
    AutoScalingRollingUpdate,
    CreationPolicy,
    ResourceSignal,
    UpdatePolicy
)
from troposphere import Base64, Join
from troposphere import Parameter, Ref, Template
from troposphere.autoscaling import AutoScalingGroup, Tag
from troposphere.autoscaling import LaunchConfiguration
from troposphere.elasticloadbalancing import LoadBalancer
from troposphere.policies import (
    AutoScalingReplacingUpdate, AutoScalingRollingUpdate, UpdatePolicy
)
t = Template()
# prints subnetid list and template to create role
t, role_id = create_prod_template(t)
t, vpcids = create_vpc(t)
t, subnetids = create_subnet(t, vpcids)
t, sg_output = create_sg(t, subnetids)
sg_output_id_list = []
for x, y in sg_output.items():
    sg_output_id_list.append(y)

subnetids_output_id_list = []
for x, y in subnetids["SubnetIds"].items():
    subnetids_output_id_list.append(y)

ref_region = Ref('AWS::Region')

AmiId = t.add_parameter(Parameter(
    "AmiId",
    Type="String",
    Default="ami-0e999cbd62129e3b1",
    Description="The AMI id for the instances",
))

KeyName = t.add_parameter(Parameter(
    "KeyName",
    Type="String",
    Description="Name of an existing EC2 KeyPair to enable SSH access",
    MinLength="1",
    AllowedPattern="[\x20-\x7E]*",
    MaxLength="255",
    Default="eks",
    ConstraintDescription="can contain only ASCII characters.",
))

ec2role = t.add_resource(Role(
    "Ec2Roletest",
    RoleName="eksworker",
    ManagedPolicyArns=["arn:aws:iam::aws:policy/service-role/AmazonEC2RoleforSSM"],
    AssumeRolePolicyDocument={
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": [
                            "ssm.amazonaws.com",
                            "ec2.amazonaws.com"
                        ]
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        },
    Path="/"
))
StackName = Ref('AWS::StackName')
region = Ref('AWS::Region')
SSMEC2 = t.add_resource(InstanceProfile(
        "SSMEC2",
        InstanceProfileName="SSM-EC2",
        Roles=[Ref("Ec2Roletest")]
    ))

LaunchConfig = t.add_resource(LaunchConfiguration(
    "LaunchConfiguration",
    UserData=Base64(Join('', [
        "#!/bin/bash\n",
        "sudo yum update -y ", "\n"
        "wget https://new-mounika.s3.amazonaws.com/splunk-8.1.2-545206cc9f70-linux-2.6-x86_64.rpm", "\n"
        "sudo yum install splunk-8.1.2-545206cc9f70-linux-2.6-x86_64.rpm -y", "\n"
        "/opt/splunk/bin/splunk start --accept-license --answer-yes --no-prompt --seed-passwd Administrator", "\n"
        "INSTANCEID=$(curl -s -m 60 http://169.254.169.254/latest/meta-data/instance-id)", "\n"
        "/opt/aws/bin/cfn-signal -e $?",
        " --resource 'autoScalingGroupSplunk'",
        " --stack ", Ref("AWS::StackName"),
        " --region ", Ref("AWS::Region"), "\n"
    ])),
    ImageId=Ref(AmiId),
    AssociatePublicIpAddress=True,
    KeyName=Ref(KeyName),
    IamInstanceProfile=Ref("SSMEC2"),
    SecurityGroups=sg_output_id_list,
    InstanceType="t2.micro",
    BlockDeviceMappings=[
        ec2.BlockDeviceMapping(
            DeviceName="/dev/xvda",
            Ebs=ec2.EBSBlockDevice(
                VolumeSize="30",
                VolumeType="gp2"
            )
        ),
    ],
))

AutoScalingGroupSplunk = t.add_resource(AutoScalingGroup(
    "autoScalingGroupSplunk",
    DesiredCapacity=1,
    MinSize=1,
    MaxSize=3,
    VPCZoneIdentifier=subnetids_output_id_list,
    Tags=[
                Tag("Name", "Splunk", True)
            ],
    LaunchConfigurationName=Ref("LaunchConfiguration"),
    UpdatePolicy=UpdatePolicy(
        AutoScalingRollingUpdate=AutoScalingRollingUpdate(
            PauseTime="PT15M",
            WaitOnResourceSignals=True,
            MinInstancesInService="1",
        )
    )
))

LaunchConfigBoomi = t.add_resource(LaunchConfiguration(
    "LaunchConfigurationBoomi",
    UserData=Base64(Join('', [
        "#!/bin/bash\n",
        "sudo yum update -y ", "\n"
        "wget https://new-mounika.s3.amazonaws.com/atom_install64.sh", "\n"
        "chmod +x atom_install64.sh", "\n"
        "./atom_install64.sh -q -console -Vusername=nkarthikreddy03@gmail.com -Vpassword=Karthik73! -VatomName=mounikaAWS -VaccountId=trainingmounikamanchikatl-5D8VFJ", "\n"
        "INSTANCEID=$(curl -s -m 60 http://169.254.169.254/latest/meta-data/instance-id)", "\n"
        "/opt/aws/bin/cfn-signal -e $?",
        " --resource 'autoScalingGroupBoomi'",
        " --stack ", Ref("AWS::StackName"),
        " --region ", Ref("AWS::Region"), "\n"
    ])),
    ImageId=Ref(AmiId),
    AssociatePublicIpAddress=True,
    KeyName=Ref(KeyName),
    IamInstanceProfile=Ref("SSMEC2"),
    SecurityGroups=sg_output_id_list,
    InstanceType="t2.micro",
))

AutoScalingGroupBoomi = t.add_resource(AutoScalingGroup(
    "autoScalingGroupBoomi",
    DesiredCapacity=1,
    MinSize=1,
    MaxSize=3,
    VPCZoneIdentifier=subnetids_output_id_list,
    LaunchConfigurationName=Ref("LaunchConfigurationBoomi"),
    Tags=[
                Tag("Name", "Boomi", True)
            ],
    UpdatePolicy=UpdatePolicy(
        AutoScalingRollingUpdate=AutoScalingRollingUpdate(
            PauseTime="PT15M",
            WaitOnResourceSignals=True,
            MinInstancesInService="1",
        )
    )
))

if __name__ == "__main__":
    template = (t.to_json())
    # print template
    f = open("network_backoffice.template", 'w+')
    f.write(template)
    f.close()
