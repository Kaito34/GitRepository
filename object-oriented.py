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
  -> Read_img
    -> BattleFlow
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
            if self.filename == 'dummy':
                pos_x,pos_y = ('dummy','dummy')
        #現在地によって機能を変える(未実装)
        return pos_x,pos_y

    @property
    def exist(self):
        return os.path.isfile(self.filename)

    @property
    def click(self):
        self.pos_x,self.pos_y =  Image_recognition(self.filename).pos()
        print(self.pos_x,self.pos_y)
        if pos_x != 'dummy':
            pg.click(self.pos_x,self.pos_y)



"""現在地を文字認識によって取得"""
class Where:
    def __init__(self,filename):
        self.__filename = filename

    def rec_url(urlnum):
        urls = ["quest_supporter_win","raid_multi_win","result_multi_win"]
        if judge_img(urls[urlnum]):
            return True


"""必要な画像インスタンスを読み込クラス
[todo] 何度も追加するのが面倒なので、手っ取り早く追加できるようにしたい"""
class Read_img:
    def __init__(self,info):
        self.l = [[] for i in range(11)]
        self.l[0] = self.ok = Image_recognition("ok.png")
        self.l[1] = self.reload = Image_recognition("reload.png")
        self.l[2] = self.bookmark = Image_recognition("bookmark_win.png")
        self.l[3] = self.quest_supporter = Image_recognition("quest_supporter_win.png")
        self.l[4] = self.raid_multi = Image_recognition("raid_multi_win.png")
        self.l[5] = self.raid = Image_recognition("raid_win.png")
        self.l[6] = self.result_multi = Image_recognition("result_multi_win.png")
        self.l[7] = self.result = Image_recognition("result_win.png")
        self.l[8] = self.quest_supporter = Image_recognition("result_multi_win.png")
        self.l[9] = self.quest_supporter = Image_recognition("result_multi_win.png")
        self.l[10] = self.attack = Image_recognition("attack.png")
        self.l[11] = self.semi = Image_recognition("semi.png")
        self.l[12] = self.full = Image_recognition("full.png")
        self.l[13] = self.summon_choice = Image_recognition("summon_choice.png")
        self.l[14] = self.attack_cancel = Image_recognition("attack_cancel.png")
        self.l[15] = self.summon_fin = Image_recognition("summon_fin.png")

        self.l[16] = self.summon_friend = Image_recognition(info['summon_friend'])
        self.l[17] = self.summon_battle = Image_recognition(info["summon_battle.png"])

        self.dummy = Image_recognition('dummy')
        self.prepare()

    """初期設定としてファイル損失やディレクトリパス指定ミス時にエラーを出す"""
    def prepare(self):
        for i in range(len(l)):
            if not self.l[i].exist:
                print(self.l[i].filename+" does not exist.")
                sys.exit()


'''フローを実行するクラス
[todo]ランダムで待機時間を設定したい'''
class BattleFlow(Read_img):
    def __init__(self,info):
        self.__R = Read_img(info)

    """固まった時の対処"""
    def if_move(self,curlist,url,duration,n):
        """
        curlist: 実行したいインスタンスを順に格納したリスト。
                 最後は遷移が成功したかチェックするためのurlを格納。
        url:     リロード・ブクマ時の戻り先url。
        duration:インスタンスの実行から遷移にかかる時間。
        n:       再帰関数の再帰回数の上限。[todo]初期設定しておく説
        """

        print("n"+str(n)+"回目")
        if n == 0:
            sys.exit()

        for num in range(len(curlist)-1):
            try:
                curlist[num].click
                time.sleep(duration[num])
                if curlist[num+1].judge():
                    pass
                elif not curlist[num+1].judge():
                    time.sleep(5)
                    if curlist[num+1].judge():
                        pass
                    else: #リロード、ブックマーク
                        self.__R.if_move([self.reload,self.bookmark,url],url,[3,4],n-1)
                        return self.__R.if_move(self,curlist,url,duration,n-1)
            except:
                self.__R.if_move([self.reload,self.bookmark,url],url,[3,4],n-1)
                return self.__R.if_move(self,curlist,url,duration,n-1)


    """フレンド選択からバトルスタートのフロー"""
    @property
    def friend_phase(self):
        #フレンド石選択→ok
        return self.__R.if_move([self.summon_friend,self.ok,self.raid_multi],self.quest_supporter,[1.5,1.5],3)

    """バトル開始から
    1. 召喚石のみ選択(1召喚石)
    2. 攻撃のみポチる(0ポチ)
    3. 召喚石を召喚した後、フルオート(1召喚フル)
    4. 攻撃を押した後、セミオート(セミ)
    5. リロ殴り
    6. 指定のアビリティ、召喚石を使用して攻撃(nポチn召喚nオート)
    """
    @property
    def attack_phase1(self):
        return
        self.__R.if_move(
        [self.dummy,self.attack],self.raid_multi,[7],3)
        ,self.__R.if_move([self.summon_choice,self.summon_battle,self.ok,self.attack,self.summon_fin],self.raid_multi,[0.5,0.5,0.5,0.5],3)
        ,self.__R.if_move([self.reload,self.bookmark],self.result_multi,[3],3)
        ,self.__R.if_move([self.bookmark,self.summon_friend],self.result_multi,[4],3)

if __name__ == "__main__":

    info = {
    'summon_friend':'summon_friend.png' ,
    'summon_battle':'rose.png',
    }

    #[todo]infoの辞書にリストを渡すと気軽に追加できるようなクラス作成


    #フレンド選択画面におけるフレンド召喚石の設定
    R = BattleFlow(info) #attack_command
    R.friend_select
    #BattleFlow('summon_friend.png').battle

    """
    #理想
    click(varuna) #フレンド選択
    click(battlestart,info) #バトル開始～終了まで
    """
