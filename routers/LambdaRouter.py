from fastapi import APIRouter
from pydantic import BaseModel
import boto3
import json
import os


LambdaRouter = APIRouter(
    prefix="/lambda"
)

class Item(BaseModel):
    ip: str

@LambdaRouter.post('/')
async def post_lambda(item: Item):
    print(item.ip)
    return 'a'


def update_waf_ipset(ipset_name,ipset_id,address_list):
    """Updates the AWS WAF IP set"""
    waf_client = boto3.client('wafv2')

    lock_token = get_ipset_lock_token(waf_client,ipset_name,ipset_id)

    waf_client.update_ip_set(
        Name=ipset_name,
        Scope='REGIONAL',
        Id=ipset_id,
        Addresses=address_list,
        LockToken=lock_token
    )

    print(f'Updated IPSet "{ipset_name}" with {len(address_list)} CIDRs')

def get_ipset_lock_token(client,ipset_name,ipset_id):
    """Returns the AWS WAF IP set lock token"""
    ip_set = client.get_ip_set(
        Name=ipset_name,
        Scope='REGIONAL',
        Id=ipset_id)
    
    return ip_set['LockToken']
