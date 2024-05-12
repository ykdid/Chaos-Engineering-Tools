import boto3
import math
import random
from botocore.exceptions import ClientError

def lambda_handler(event, context):

    s3 = boto3.resource('s3')
    obj = s3.Object('config--bucket', 'sgconfig.txt')
    body = obj.get()['Body'].read().decode('UTF-8')
    config_elems = body.split('\n')[1:]
    config_elems = [elem.split(" ") for elem in config_elems][:-1]
    
    
    client = boto3.client('ec2')
    print(config_elems)
    for i in range(len(config_elems)):
        elem = config_elems[i]
        
        try:
            response = client.describe_security_groups(
                GroupIds=[
                    elem[0],
                ],
            )
            rule_list = response['SecurityGroups'][0]['IpPermissions']
            
            protocol = random.choice(['tcp', 'udp'])
            state = random.choice(['open', 'close'])
            port = random.choice(range(65536))
            cidr = str(random.choice(range(256)))+'.'+str(random.choice(range(256)))+'.'+str(random.choice(range(256)))+'.'+str(random.choice(range(256)))+'/'+str(random.choice(range(33)))
            print("state", state)
            
            if state=="open":
                client.authorize_security_group_ingress(GroupId=elem[0],IpProtocol=protocol,CidrIp=cidr,FromPort=port,ToPort=port)
            else:
                rule=random.choice(rule_list)
                print(rule)
                client.revoke_security_group_ingress(GroupId=elem[0],IpProtocol=rule['IpProtocol'],CidrIp=rule['IpRanges'][0]['CidrIp'],FromPort=rule['FromPort'],ToPort=rule['ToPort'])
      
        except ClientError as e:
            print(e)

