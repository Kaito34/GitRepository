# encoding: utf_8

import pyautogui as pg
import os
import sys
import random
import time

pg.PAUSE = 0.02

"""""""""""""""""""""""""""""""""
#分岐アルゴリズム
指定画像の検索
Y→ボタンをクリック
N→段階的に画像検証していく

様々な行動パターンがある中で一つに関数をまとめて使いまわすのは良くない
→それぞれの行動パターンに関してクラスを作成する
"""""""""""""""""""""""""""""""""

"""画像が収納されているパスの指定"""
os.chdir("/Users/kusumotokaito/Downloads/granblue")

"""グローバル変数"""
regionbox = (0,0,1000,1500)

#macのズレを修正
def convert(x1,y1):
    x2=x1*0.5178
    y2=y1*0.50088
    return x2,y2

"""
Image_recognition
  ->
"""

"""
画像の読み込み、クリックを実行するクラス

[TODO]
スクリーンショットを撮った後、機械学習を用いて画像認識する
初回起動の位置合わせ後は座標を記録して所要時間削減する
"""

class Image_recognition:
    """
    judge: 画像があるか判断しTrueかFalseで返す
    pos: 画像の座標を返す
    click: 画像の座標をクリックする
    """
    def __init__(self,filename):
        self.__filename = filename

    def judge(self):
        if pg.locateCenterOnScreen(self.__filename,confidence=0.8,region=regionbox):
            return True
        else:
            return False

    def pos(self):
        # openCVを用いて範囲内に画像があるか調べる
        #文字認識も有効
        try:
            pos_x,pos_y = pg.locateCenterOnScreen(self.__filename,confidence=0.8,region=regionbox)
        except:
            pos_x,pos_y = (None,None)
        #現在地によって機能を変える(未実装)
        return pos_x,pos_y

    @property
    def click(self):
        try:
            self.__pos_x,self.__pos_y =  Image_recognition(self.__filename).pos()
            print(self.__pos_x,self.__pos_y)
            pg.click(self.__pos_x,self.__pos_y)
            return True
        except:
            return False


"""現在地を文字認識によって取得"""
class Where:
    def __init__(self,filename):
        self.__filename = filename

    def rec_url(urlnum):
        urls = ["quest_supporter_win","raid_multi_win","result_multi_win"]
        if judge_img(urls[urlnum]):
            return True


"""フローの実行クラス"""
class BattleFlow:
    def __init__(self,friend_summon):
        self.friend_summon = friend_summon

    """フレンド選択までのフロー"""

    """フレンド選択からバトルスタートのフロー"""
    def friend_select(self):
        sf =0


if __name__ == "__main__":

    bookmark = Image_recognition("bookmark.png")
    bookmark



    if not quest_supporter.judge_img(): #quest_supporterがない時
        bookmark.click #bookmarkに移動　#固まった時の対応
    varuna.click #フレ選択
    ok.click

    """
    #理想
    click(varuna) #フレンド選択
    click(battlestart,info) #バトル開始～終了まで
    """
