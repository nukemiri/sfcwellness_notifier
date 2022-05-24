# -*- coding: utf-8 -*-

import requests
import os
from bs4 import BeautifulSoup
import pickle
from pprint import pprint
import json
from pathlib import Path
import datetime



url = "https://wellness.sfc.keio.ac.jp/v3/index.php"
empty_url = "https://wellness.sfc.keio.ac.jp/v3/index.php?page=reserve&limit=9999"
session = requests.session()
login_data = {
    'UTF-8': '✓',
    'login': os.environ.get("CNS_LOGIN_ID"),
    'password': os.environ.get("CNS_LOGIN_PASSWORD"),
    'submit':"login",
    "page":"top",
    "mode":"login",
    }
login = session.post(url, data=login_data)
response = session.get(empty_url)

soup = BeautifulSoup(response.text, 'html.parser')
table = soup.find_all("table")[1].tbody

rows = table.find_all('tr')
empty_list = []
for row in rows:
    column = []   
    for td in row.find_all("td"):
        column.append(td.text.replace('\r', '').replace('\n', '').replace('\u3000', ''))
    empty_list.append(column)

for i in range(len(empty_list)):
    if empty_list[i][0] == "":
        empty_list[i][0] = empty_list[i-1][0]
        if empty_list[i][1] == "":
            empty_list[i][1] = empty_list[i-1][1]
    if empty_list[i][9] == "向き":
        empty_list[i][9] = "運動制限向き"
    elif empty_list[i][9] == "限定":
        empty_list[i][9] = "運動制限限定"
# [0日時,1時限,2種目名,3教員名,4シラバスリンク,5実施形態,6場所,7開講言語,8運動強度,9運動制限,10空き,11予約リンク]
# pprint(empty_list)

myfile = Path(os.path.join(os.path.dirname(__file__),"lastempty.txt"))
myfile.touch(exist_ok=True)

f = open(os.path.join(os.path.dirname(__file__),"lastempty.txt"),"rb")
try:
    last_empty = pickle.load(f)
except:
    last_empty = []

f = open(os.path.join(os.path.dirname(__file__),"lastempty.txt"),"wb")
pickle.dump(empty_list,f)

notify_list = []

for i in empty_list:
    if i[:4] in [j[:4] for j in last_empty]:
        pass
    else:
        notify_list.append(i)

pprint(notify_list)

if len(notify_list)>0:
    # 通知する
    if os.environ.get("WELLNESS_NOTIFIER_WEBHOOK_URL") != None:
        dt_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        for i in notify_list:
            webhook_url  = os.environ.get("WELLNESS_NOTIFIER_WEBHOOK_URL")
            main_content = {'content': f"""
{i[0]}{i[1]}『{i[2]}』が予約可能になりました。
場所:{i[6]} 強度:{i[8]} {i[9]} [{dt_now.strftime('%H:%M')}]
https://wellness.sfc.keio.ac.jp/
            """}
            headers      = {'Content-Type': 'application/json'}
            response     = requests.post(webhook_url, json.dumps(main_content), headers=headers)
