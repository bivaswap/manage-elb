#!/usr/bin/python

# Version 1.0
# Author : Bivas Mandal


import boto3, sys, argparse, os
from termcolor import colored, cprint

parser = argparse.ArgumentParser()
parser.add_argument('--instanceId', help='Enter instance ID')
parser.add_argument('--stackName', help='Enter instance ID')
args = parser.parse_args()

elb = boto3.client('elb')
ec2 = boto3.client('ec2')

# Pull Instance-ELB relation
def GetInstancesRelation():
    instances = {}
    response = elb.describe_load_balancers()
    for i in range(0,len(response['LoadBalancerDescriptions'])):
        for j in range(0,len(response['LoadBalancerDescriptions'][i]['Instances'])):
            instances[response['LoadBalancerDescriptions'][i]['Instances'][j]['InstanceId']] = response['LoadBalancerDescriptions'][i]['LoadBalancerName']
    return instances

# Count running instance in a stack
def countActiveInstance(name):
    response = ec2.describe_instances(
        Filters=[
            {'Name': 'tag:Name','Values': [name]},
            {'Name': 'instance-state-name', 'Values': ['running']}
            ],
    )
    return len(response['Reservations'])

# Count running instance 
def countInServiceInstance(LoadBalancerName):
    elb = boto3.client('elb')
    response = elb.describe_instance_health(LoadBalancerName = LoadBalancerName)
    count = 0
    for i in range(0,len(response['InstanceStates'])):
        if(response['InstanceStates'][0]['State'] == 'InService'):
            count += 1
    return count

def removeFromELB(ELBName, instanceId):        
    responseRemove = elb.deregister_instances_from_load_balancer(
        LoadBalancerName= ELBName,
        Instances=[{'InstanceId': instanceId},]
    )
    print responseRemove

def addToELB(ELBName, instanceId):        
    responseRemove = elb.register_instances_with_load_balancer(
        LoadBalancerName= ELBName,
        Instances=[{'InstanceId': instanceId},]
    )
    print responseRemove


def getPublicDnsName(instanceId):
    response = ec2.describe_instances(InstanceIds = ['i-046ca212822da0d57'])
    return response['Reservations'][0]['Instances'][0]['PublicDnsName']

InstanceAndELB = GetInstancesRelation()

print 'The stack '+ colored(args.stackName,'red') + ' has ' + colored(str(countActiveInstance(args.stackName)), 'red') + ' running instances \nLoadbalancer ' + colored(InstanceAndELB.get(args.instanceId),'green') + ' has ' + colored(str(countInServiceInstance(InstanceAndELB.get(args.instanceId))),'red') + ' In-Service instances'

while True:
    choice = raw_input('Do you want to remove the instance from loadbalancer? [y/n]')
    if(choice == 'y' or choice == 'Y'):
        print colored(getPublicDnsName(args.instanceId),'green')
        removeFromELB(InstanceAndELB.get(args.instanceId),args.instanceId)
        
        choice2 = raw_input('Do you want to add the instance back to loadbalancer? [y/n]')
        while True:
            if(choice2 == 'y' or choice2 == 'Y'):
                addToELB(InstanceAndELB.get(args.instanceId),args.instanceId)
                print 'Added'
                break
            elif(choice2 == 'n' or choice2 == 'N'):
                print 'Exiting ..'
                break
            else:
                 print 'Please respond with "y/n"'                    
    elif(choice == 'n' or choice == 'N'):
        print 'Exiting...'
        break
    else:
        print 'Please respond with "y/n"'

print 'The stack '+ colored(args.stackName,'red') + ' has ' + colored(str(countActiveInstance(args.stackName)), 'red') + ' running instances \nLoadbalancer ' + colored(InstanceAndELB.get(args.instanceId),'green') + ' has ' + colored(str(countInServiceInstance(InstanceAndELB.get(args.instanceId))),'red') + ' In-Service instances'
