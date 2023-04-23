from fastapi import APIRouter
from fastapi import Request
import json
import os
from dotenv import load_dotenv
import pymysql

load_dotenv()

SlackRouter = APIRouter(
	prefix="/slack"
)

@SlackRouter.post('/ban_list')
async def post_ban_list(request: Request):
	con = pymysql.connect(
		host = os.environ['DATABASE_HOST'].strip(),
		user = os.environ['DATABASE_USER'].strip(),
		password = os.environ['DATABASE_PASSWORD'].strip(),
		db = os.environ['DATABASE_DB'].strip(),
		charset='utf8mb4'
	)

	template = {
		"blocks": [
			{
				"type": "header",
				"text": {
					"type": "plain_text",
					"text": "금지된 ip 리스트를 출력합니다."
				}
			},
			{
				"type": "divider"
			},
		]
	}
	cur = con.cursor()
	sql = "select * from ban_list"
	cur.execute(sql)
	rows = cur.fetchall()
	for element in rows:
		template["blocks"].append({
			"type": "section",
			"text": {
				"type": "plain_text",
				"text": element[0]
			}
		})
		
	return template


@SlackRouter.post('/require')
async def post_require(request: Request):
	return {"h":"a"}

# form_data = await request.form()
# json_data = json.dumps({key: form_data.getlist(key)[0] for key in form_data.keys()})
# print(json_data)