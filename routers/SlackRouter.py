from fastapi import APIRouter
from fastapi import Request
import os
from dotenv import load_dotenv
import pymysql
import boto3

load_dotenv()

SlackRouter = APIRouter(
	prefix="/slack"
)

IPV4_SET_NAME=os.environ['IPV4_SET_NAME'].strip()
IPV4_SET_ID=os.environ['IPV4_SET_ID'].strip()

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
					"text": "차단한 ip 리스트를 출력합니다."
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

	cur.close()
	con.close()
		
	return template


@SlackRouter.post('/require')
async def post_require(request: Request):
	
	form_data = await request.form()
	
	con = pymysql.connect(
		host = os.environ['DATABASE_HOST'].strip(),
		user = os.environ['DATABASE_USER'].strip(),
		password = os.environ['DATABASE_PASSWORD'].strip(),
		db = os.environ['DATABASE_DB'].strip(),
		charset='utf8mb4'
	)
	cur = con.cursor()
	sql = "delete from ban_list where ip='"+ form_data.get('text') + "'"
	cur.execute(sql)
	sql = "select * from require_list where ip='" + form_data.get('text') + "'"
	cur.execute(sql)
	row_result = cur.rowcount
	if row_result == 0:
		sql = "insert into require_list values ('"+ form_data.get('text') +"', '', current_timestamp)"
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
	try:
		Address_list.remove(form_data.get('text')+"/32")
		lock_token = response['LockToken']
		response = client.update_ip_set(
			Name = IPV4_SET_NAME,
			Scope = 'REGIONAL',
			Id = IPV4_SET_ID,
			Description = 'string',
			Addresses = Address_list,
			LockToken=lock_token
		)
		return "성공"
	except:
		return "해당 ip가 없습니다."
	


@SlackRouter.post('/require_list')
async def post_require_list():
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
					"text": "허용된 ip 리스트를 출력합니다."
				}
			},
			{
				"type": "divider"
			},
		]
	}
	cur = con.cursor()
	sql = "select * from require_list"
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

	cur.close()
	con.close()
		
	return template
	
# form_data = await request.form()
# json_data = json.dumps({key: form_data.getlist(key)[0] for key in form_data.keys()})
# print(json_data)