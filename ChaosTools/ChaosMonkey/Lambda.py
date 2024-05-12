import boto3
import math
import random
from datetime import datetime as dt
from datetime import timezone

def lambda_handler(event, context):
    now = dt.now(timezone.utc)
    hr = now.hour
    minu = now.minute
    hr = (hr+int((minu+30)/60)+5)%24
    minu = (minu+30)%60
    if minu<=9:
        currtime = int(str(hr)+'0'+str(minu)) 
    else:
        currtime = int(str(hr)+str(minu)) 
    print(currtime)
    #current time 

    s3 = boto3.resource('s3') #access to Amazon S3 service in Python applications using the AWS SDK
    obj = s3.Object('config--bucket', 'config.txt') #reads config txt from s3 bucket
    body = obj.get()['Body'].read().decode('UTF-8')
    config_elems = body.split('\n')[1:]
    config_elems = [elem.split(" ") for elem in config_elems]
    
    client = boto3.client('ecs') #Creates an ECS client to access the Amazon ECS (Elastic Container Service) service.
    for i in range(len(config_elems)):
        elem = config_elems[i]
        if int(elem[2])<=currtime and int(elem[3])>=currtime:
            print("in period")
            ld = client.list_container_instances(cluster=elem[0], status='DRAINING')['containerInstanceArns']
            if len(ld)==0:
                l = client.list_container_instances(cluster=elem[0], status='ACTIVE')['containerInstanceArns']
                count_for_shutdown = math.floor(len(l)*int(elem[1])/100)
                print(count_for_shutdown)
                inst_list = random.sample(l,count_for_shutdown)
                resp = client.update_container_instances_state(cluster=elem[0],containerInstances=inst_list,status='DRAINING')
                print(resp)
        else:
            print("not in period")
            ld = client.list_container_instances(cluster=elem[0], status='DRAINING')['containerInstanceArns']
            if len(ld)>0:
                client.update_container_instances_state(cluster=elem[0],containerInstances=ld,status='ACTIVE')

