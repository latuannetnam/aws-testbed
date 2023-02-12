import boto3
import os
import json
from datetime import datetime, timezone, tzinfo

ec2client = boto3.client('ec2')
max_runtime = int(os.environ.get('MAX_RUNTIME', '3600'))
sns_topicARN = os.environ.get('SNS_TOPIC','')
sns_message={}

def lambda_handler(event, context):
    # Get a list of all running EC2 instances
    running_instances = ec2client.describe_instances(Filters=[{
            'Name': 'instance-state-name',
            'Values': ['running']
        }])
    current_time = datetime.now(timezone.utc)
    # Iterate through all running instances
    for reservation in running_instances["Reservations"]:
      for instance in reservation["Instances"]:    
            # Get the time that the instance has been running
        launch_time = instance["LaunchTime"]
        time_diff = current_time - launch_time
        runtime = time_diff.total_seconds()
        state = instance["State"]["Name"]
        can_terminate = True
        if 'Tags' in instance:
            for tag in instance["Tags"]:
                # if tag["Key"] == "TerminalProtection" and (tag["Value"] == "Yes" or tag["Value"] == "On" or tag["Value"] == "1"):
                if tag["Key"] == "TerminalProtection" and (tag["Value"] == "Yes" or tag["Value"] == "On" or tag["Value"] == "1"):
                    can_terminate = False
                    break

        # print("state:", state, "run time:", runtime, "can_terminate:", can_terminate)
        instance_id = instance["InstanceId"]
        if state=="running" and runtime>= max_runtime and can_terminate:
            print("Terminate instance:", instance_id)
            try:
                ec2client.terminate_instances(InstanceIds=[instance_id])
                sns_message[instance_id] = "Terminated"
            except Exception  as e:
                print("Can not terminate instance:", instance["InstanceId"], "reason:", e)
                sns_message[instance_id] = "Try to Terminate but failed with reason:" + str(e)
        if sns_message and sns_topicARN:
            sns_client = boto3.client('sns', region_name='ap-southeast-1')
            resp = sns_client.publish(
                TopicArn=sns_topicARN,
                Message=json.dumps({'default': json.dumps(sns_message, indent=4)}),
                Subject='Server Shutdown Warning',
                MessageStructure='json'
            )
    return {
        'statusCode': 200,
        'body': json.dumps('ok')
    }