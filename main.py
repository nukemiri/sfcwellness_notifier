# -*- coding: utf-8 -*-

from re import A
import requests
import os
from bs4 import BeautifulSoup
import pickle
from pprint import pprint
import json
from pathlib import Path
import datetime
# import tweepy
import config



url = "https://wellness.sfc.keio.ac.jp/v3/index.php?page=reserve&limit=9999"

response = requests.get(url)

soup = BeautifulSoup(response.text, 'html.parser')
table = soup.find_all("table")[1].tbody


rows = table.find_all('tr')
empty_list = []
for row in rows:
    column = []
    tr = row.find_all("td")
    for td in tr:
        column.append(td.text.replace('\r', '').replace('\n', '').replace('\u3000', ''))
    empty_list.append(column)

"""<td class="w3-hide-small center"></td>
<td class="w3-hide-small center"></td>
<td class="w3-hide-small">体操</td>
<td class="w3-hide-small">久永　将太</td>
<td class="w3-hide-small center"><small>SFCアリーナ</small></td>
<td class="w3-hide-small center">中</td>
<td class="w3-hide-large w3-hide-medium"><strong>日時:</strong> 6月7日(火) 3限<br/><strong>種目:</strong> 体操<br/><strong>教員:</strong> 久永　将太<br/><strong>場所:</strong> SFCアリーナ<br/><strong>運動強度:</strong> 中</td>
<td class="center">10</td>"""

pprint(empty_list)

for i in range(len(empty_list)):
    if empty_list[i][0] == "":
        empty_list[i][0] = empty_list[i-1][0]
        if empty_list[i][1] == "":
            empty_list[i][1] = empty_list[i-1][1]
# [0日付,1時限,2種目名,3教員名,4場所,5運動強度,6'日時: 6月8日(水) 5限種目: フェンシング教員: 冨田智子場所: SFC剣道場運動強度: 中',7空き]
pprint(empty_list)

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
    dt_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))

    # if config.ACCESS_TOKEN != "":
    #         CK = config.CONSUMER_KEY
    #         CS = config.CONSUMER_SECRET
    #         AT = config.ACCESS_TOKEN
    #         AS = config.ACCESS_TOKEN_SECRET
    #         auth = tweepy.OAuthHandler(CK, CS)
    #         auth.set_access_token(AT, AS)
    #         api = tweepy.API(auth)

    for i in notify_list:
        message = f"""
{i[0]}{i[1]}『{i[2]}』が予約可能になりました。
場所:{i[4]} 強度:{i[5]} [{dt_now.strftime('%H:%M')}]
https://wellness.sfc.keio.ac.jp/
    """
        if config.DISCORD_WEBHOOK != "":
            
            webhook_url  = config.DISCORD_WEBHOOK
            main_content = {'content': message}
            headers      = {'Content-Type': 'application/json'}
            response     = requests.post(webhook_url, json.dumps(main_content), headers=headers)
        # if config.ACCESS_TOKEN != "":
        #     api.update_status(message)
    