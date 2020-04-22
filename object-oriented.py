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
os.chdir(r"C:\Users\Kaito Kusumoto\Documents\Python Scripts\グラブル\images")

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
        self.filename = filename

    def judge(self):
        if pg.locateCenterOnScreen(self.filename,confidence=0.8,region=regionbox):
            return True
        else:
            return False

    def pos(self):
        # openCVを用いて範囲内に画像があるか調べる
        #文字認識も有効
        try:
            pos_x,pos_y = pg.locateCenterOnScreen(self.filename,confidence=0.8,region=regionbox)
        except:
            pos_x,pos_y = (None,None)
        #現在地によって機能を変える(未実装)
        return pos_x,pos_y

    @property
    def exist(self):
        return os.path.isfile(self.filename)

    @property
    def click(self):
        self.pos_x,self.pos_y =  Image_recognition(self.filename).pos()
        print(self.pos_x,self.pos_y)
        pg.click(self.pos_x,self.pos_y)



"""現在地を文字認識によって取得"""
class Where:
    def __init__(self,filename):
        self.__filename = filename

    def rec_url(urlnum):
        urls = ["quest_supporter_win","raid_multi_win","result_multi_win"]
        if judge_img(urls[urlnum]):
            return True


"""フローの実行クラス"""
class BattleFlow():
    def __init__(self,summon_friend='summon_friend.png'):
        self.l = []
        self.l.append(self.summon_friend = Image_recognition(summon_friend))
        self.l.append(self.ok = Image_recognition("ok.png"))
        self.l.append(self.reload = Image_recognition("reload.png"))
        self.l.append(self.bookmark = Image_recognition("bookmark_win.png"))
        self.l.append(self.quest_supporter = Image_recognition("quest_supporter_win.png"))
        self.l.append(self.raid_multi = Image_recognition("raid_multi_win.png"))
        self.l.append(self.raid = Image_recognition("raid_win.png"))
        self.l.append(self.result_multi = Image_recognition("result_multi_win.png"))
        self.l.append(self.result = Image_recognition("result_win.png"))
        self.l.append(self.quest_supporter = Image_recognition("result_multi_win.png"))
        self.l.append(self.quest_supporter = Image_recognition("result_multi_win.png"))

        self.stopper = 0
        self.prepare()

    def prepare(self):
        for i in range(1,len(self.l)):
            if not self.l[i].exist:
                print(self.l[i].filename+" does not exist.")
                sys.exit()

    """固まった時の対処"""
    def if_move(self,curlist,url,duration=0):
        self.stopper += 1
        if self.stopper > 2:
            sys.exit()
        for num in range(len(curlist)-1):
            try:
                curlist[num].click
                time.sleep(duration)
                if curlist[num+1].judge():
                    pass
                elif not curlist[num+1].judge(): #curlist[num+1]がない時
                    time.sleep(5)
                    if curlist[num+1].judge():
                        pass
                    else:
                        if_move([self.reload,self.bookmark,url],url,0.5)
                        return if_move(self,curlist,url,duration=0)
            except:
                BattleFlow(self.summon_friend).if_move([self.reload,self.bookmark,url],url,0.5)
                return BattleFlow(self.summon_friend).if_move(self,curlist,url,duration)

    """フレンド選択からバトルスタートのフロー"""
    @property
    def friend_select(self):
        return BattleFlow(self.summon_friend).if_move([self.summon_friend,self.ok,self.raid_multi],self.quest_supporter,1)



if __name__ == "__main__":

    BattleFlow('summon_friend.png').friend_select
    #BattleFlow('summon_friend.png').battle

    """
    #理想
    click(varuna) #フレンド選択
    click(battlestart,info) #バトル開始～終了まで
    """
