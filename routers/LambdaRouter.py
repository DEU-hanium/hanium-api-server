from fastapi import APIRouter
from pydantic import BaseModel
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

IPV4_SET_NAME=os.environ['IPV4_SET_NAME'].strip()
IPV4_SET_ID=os.environ['IPV4_SET_ID'].strip()

LambdaRouter = APIRouter(
    prefix="/lambda"
)

class Item(BaseModel):
    ip: str

@LambdaRouter.post('/')
async def post_lambda(item: Item):
    client = boto3.client('wafv2', region_name = 'ap-northeast-2')

    response = client.get_ip_set(
        Name=IPV4_SET_NAME,
        Scope='REGIONAL',
        Id=IPV4_SET_ID
    )
    Address_list = response["IPSet"]["Addresses"]
    Address_list.append(item.ip)
    lock_token = get_ipset_lock_token(client, IPV4_SET_NAME,IPV4_SET_ID)
    response = client.update_ip_set(
        Name = IPV4_SET_NAME,
        Scope = 'REGIONAL',
        Id = IPV4_SET_ID,
        Description = 'string',
        Addresses = Address_list,
        LockToken=lock_token
    )
    print(response)
    return

def get_ipset_lock_token(client,ipset_name,ipset_id):
    """Returns the AWS WAF IP set lock token"""
    ip_set = client.get_ip_set(
        Name=IPV4_SET_NAME,
        Scope='REGIONAL',
        Id=IPV4_SET_ID
    )
    
    return ip_set['LockToken']