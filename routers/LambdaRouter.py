from fastapi import APIRouter
from pydantic import BaseModel
import boto3
import os
from dotenv import load_dotenv
import requests

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
    lock_token = response['LockToken']
    response = client.update_ip_set(
        Name = IPV4_SET_NAME,
        Scope = 'REGIONAL',
        Id = IPV4_SET_ID,
        Description = 'string',
        Addresses = Address_list,
        LockToken=lock_token
    )
    print(response)

    template = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "해당 IP가 차단되었습니다."
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": item.ip
                }
            }
        ]
    }

    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {os.environ['SLACK_TOKEN'].strip()}",
        "Content-Type": "application/json"
    }
    payload = {
        "channel": "#crawling-channel",
        "blocks": template["blocks"]
    }

    response = requests.post(url, headers=headers, json=payload)
    print(response.json())

    return