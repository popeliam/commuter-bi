from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import Sheets.credBuilder as cb
import psycopg2

sheetId = 'YOUR-SHEET-ID'
dataRange = 'Sheet1!a:z'
creds = cb.creds()
conn = psycopg2.connect(host='localhost',database='postgres',user='postgres',password='password')
cur = conn.cursor()
values = []

def colList(n):
	return n.name

def strList(n):
	if not n:
		return ''
	else:
		return str(n)

def getData():
	global values
	cur.execute('''	SELECT * 
		FROM commute_datasource
		WHERE extract(dow from departure_ts) between 1 and 5
		''')
	queryData = cur.fetchall()
	values = []
	values.append(list(map(colList,cur.description)))
	for i in queryData:
		values.append(list(map(strList,i)))

def update():
	global values
	service = build('sheets','v4',credentials=creds)
	sheet = service.spreadsheets()
	body = {'values':values}
	if len(values) > 1:
		clear = sheet.values().clear(spreadsheetId=sheetId,range=dataRange).execute()
		result = sheet.values().update(spreadsheetId=sheetId,range=dataRange,body=body,valueInputOption='RAW').execute()

def run():
	getData()
	update()