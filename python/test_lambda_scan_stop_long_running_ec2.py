import boto3
from datetime import datetime, timezone, tzinfo

ec2 = boto3.client('ec2')

def lambda_handler(event, context):
    # Get a list of all running EC2 instances
    running_instances = ec2.describe_instances(Filters=[{
            'Name': 'instance-state-name',
            'Values': ['running']
        }])
    
    # Iterate through all running instances
    for instance in running_instances['Reservations']:
        for i in instance['Instances']:
            # Get the time that the instance has been running
            instance_time = i['LaunchTime']
            # Check if the instance has been running for more than 24 hours
            if (datetime.now(timezone.utc) - instance_time).days > 1:
                # Stop the instance
                ec2.stop_instances(InstanceIds=[i['InstanceId']])
                print("Stopped instance: ", i['InstanceId'])