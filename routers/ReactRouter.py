from fastapi import APIRouter
from fastapi import Request
import os
from dotenv import load_dotenv
import pymysql
import boto3
import requests

load_dotenv()

IPV4_SET_NAME=os.environ['IPV4_SET_NAME'].strip()
IPV4_SET_ID=os.environ['IPV4_SET_ID'].strip()

ReactRouter = APIRouter(
    prefix="/react"
)

@ReactRouter.get('/')
async def ban(request: Request):
    con = pymysql.connect(
        host = os.environ['DATABASE_HOST'].strip(),
        user = os.environ['DATABASE_USER'].strip(),
        password = os.environ['DATABASE_PASSWORD'].strip(),
        db = os.environ['DATABASE_DB'].strip(),
        charset='utf8mb4'
    )
    try:
        cur = con.cursor()
        sql = "insert into ban_list values('"+request.client.host+"', '4', current_timestamp)"
        cur.execute(sql)
        con.commit()
        cur.close()
        con.close()

        client = boto3.client('wafv2', region_name = 'ap-northeast-2')
        response = client.get_ip_set(
            Name=IPV4_SET_NAME,
            Scope='REGIONAL',
            Id=IPV4_SET_ID
        )

        Address_list = response["IPSet"]["Addresses"]
        Address_list.append(request.client.host+"/32")
        lock_token = response['LockToken']

        response = client.update_ip_set(
            Name = IPV4_SET_NAME,
            Scope = 'REGIONAL',
            Id = IPV4_SET_ID,
            Description = 'string',
            Addresses = Address_list,
            LockToken=lock_token
        )
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
                        "text": request.client.host
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
            "channel": "#crawling",
            "blocks": template["blocks"]
        }

        response = requests.post(url, headers=headers, json=payload)
        return "OK"

    except:
        return "ERROR"