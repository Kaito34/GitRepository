# coding: UTF-8

import requests
from bs4 import BeautifulSoup
import re
import pyperclip
import pyautogui as pg
import time
import random
import json
import pygame.mixer
import os

"""画像が収納されているパスの指定"""
os.chdir(r"C:\Users\Kaito Kusumoto\Documents\Python Scripts\グラブル\images")



'''スクレイピングをするクラス'''
class scraping:
    def __init__(self,battlename):
        url_dict ={
            "アバターhl" : 'https://search.yahoo.co.jp/realtime/search?ei=UTF-8&fr=rts_top&aq=0&oq=%E3%82%A2%E3%83%90%E3%82%BF%E3%83%BC&at=s&ts=41854&p=%E3%82%A2%E3%83%90%E3%82%BF%E3%83%BC+lv120+%E5%8F%82%E6%88%A6id&meta=vc%3D',
            "セレストhl": "https://search.yahoo.co.jp/realtime/search?ei=UTF-8&fr=rts_top&aq=1&oq=%E3%81%9B%E3%82%8C&at=s&ts=53296&p=%E3%82%BB%E3%83%AC%E3%82%B9%E3%83%88+%E3%83%9E%E3%82%B0%E3%83%8A+lv100+%E5%8F%82%E6%88%A6id&meta=vc%3D",
            "シヴァhl" : "https://search.yahoo.co.jp/realtime/search?p=%E3%82%B7%E3%83%B4%E3%82%A1+lv120+%E5%8F%82%E6%88%A6id&ei=UTF-8&fr=rts_top",
            "ルシファーn" : "https://search.yahoo.co.jp/realtime/search?p=%E3%83%AB%E3%82%B7%E3%83%95%E3%82%A1%E3%83%BC+%E5%8F%82%E6%88%A6id+lv150&ei=UTF-8&fr=rts_top",
            "グランデ" : "https://search.yahoo.co.jp/realtime/search?p=%E3%82%B0%E3%83%A9%E3%83%B3%E3%83%87+lv100+%E5%8F%82%E6%88%A6id&ei=UTF-8&fr=rts_top",
            "リンドヴルム" : "https://search.yahoo.co.jp/realtime/search?p=%E3%83%AA%E3%83%B3%E3%83%89%E3%83%B4%E3%83%AB%E3%83%A0+%E5%8F%82%E6%88%A6id&ei=UTF-8&fr=rts_top",
            "オリヴィエhl" : "https://search.yahoo.co.jp/realtime/search?p=%E3%82%AA%E3%83%AA%E3%83%B4%E3%82%A3%E3%82%A8+lv120+%E5%8F%82%E6%88%A6id&ei=UTF-8&fr=rts_top",
            "アヌビスhl" : "https://search.yahoo.co.jp/realtime/search?p=%E3%82%A2%E3%83%8C%E3%83%93%E3%82%B9+lv120+%E5%8F%82%E6%88%A6id&ei=UTF-8&fr=rts_top"
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
        self.ids_b = [0 for i in range(5)]
        while True:
            #リンクの取得
            #Requestsを使って、webから取得
            r = requests.get(self.target_url)

            #要素を抽出
            soup = BeautifulSoup(r.text, 'lxml')

            self.ids = []
            for i in range(5):
                elem = soup.find_all('h2')[i].contents[0]
                regex = re.compile(r"(\w{8})")
                mo = regex.search(elem)
                try:
                    self.id = mo.group(0)
                    self.ids.append(self.id)
                except:
                    pass


            #前回取得と被っていないものを取得、クリップボードへ
            for j in range(len(self.ids_b )):
                for i in range(len(self.ids)):
                        if self.ids[i] != self.ids_b [j]:
                            self.id = self.ids[i]

            print(self.id)
            pyperclip.copy(self.id)
            time.sleep(10)

            return self.id


    '''idを入力する(BattleFlowクラスを使える)'''
    def enter_id(self):
        id = self.get_id(battlename)
        pyperclip.copy()
        #bookmark click
        #enter id click
        #id box click
        #paste
        #join a room

for i in range(100):
    S = scraping("アヌビスhl")
    S.get_id()
pygame.mixer.init()
pygame.mixer.music.load("info-girl1-syuuryou1.mp3")
pygame.mixer.music.play(1)
