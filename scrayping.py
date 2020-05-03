# coding: UTF-8

import requests
from bs4 import BeautifulSoup
import re
import pyperclip
import pyautogui as pg
import time
import random
import json


'''スクレイピングをするクラス'''
class scraping:
    def __init__(self,battlename)
        url_dict =
        {
            "アバターhl" : 'https://search.yahoo.co.jp/realtime/search?ei=UTF-8&fr=rts_top&aq=0&oq=%E3%82%A2%E3%83%90%E3%82%BF%E3%83%BC&at=s&ts=41854&p=%E3%82%A2%E3%83%90%E3%82%BF%E3%83%BC+lv120+%E5%8F%82%E6%88%A6id&meta=vc%3D',
            "セレストhl": "https://search.yahoo.co.jp/realtime/search?ei=UTF-8&fr=rts_top&aq=1&oq=%E3%81%9B%E3%82%8C&at=s&ts=53296&p=%E3%82%BB%E3%83%AC%E3%82%B9%E3%83%88+%E3%83%9E%E3%82%B0%E3%83%8A+lv100+%E5%8F%82%E6%88%A6id&meta=vc%3D"
        }

        self.target_url=url_dict[battlename]

    #slackに送信
    def send_slack(self,text):
        #DO
        WEB_HOOK_URL = "https://hooks.slack.com/services/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"
        requests.post(WEB_HOOK_URL, data = json.dumps({
                        'text': text
                        }))

    '''スクレイピングでマルチidを取得、コピー。'''
    def get_id(self):
        #リンクの取得
        #Requestsを使って、webから取得
        r = requests.get(target_url)

        #要素を抽出
        soup = BeautifulSoup(r.text, 'lxml')

        elem = soup.find_all('h2')[1].contents[0][-10:-2]
        elem2 = soup.find_all('h2')[1].contents[0]
        print(elem)
        print(elem2)

        #要素を抽出\n",
        soup = BeautifulSoup(r.text, 'lxml')


        ids = []
        for i in range(5):
            elem = soup.find_all('h2')[i].contents[0]
            regex = re.compile(r"(w{8})")
            mo = regex.search(elem)
            try:
                id = mo.group(0)
                ids.append(id)
            except:
                pass
                print(id)

        #前回取得と被っていないものを取得、クリップボードへ
        for j in range(len(ids_b)):
            for i in range(len(ids)):
                    if ids[i] != ids_b[j]:
                        id = ids[i]

        pyperclip.copy(id)

        return id


    '''idを入力する(BattleFlowクラスを使える)'''
    def enter_id(self)
        id = self.get_id(battlename)
        pyperclip.copy()
        #bookmark click
        #enter id click
        #id box click
        #paste
        #join a room

while True:
    S = scraping("セレストhl")
    S.get_id()
