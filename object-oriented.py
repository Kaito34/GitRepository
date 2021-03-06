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

    @property
    def judge(self):
        if pg.locateCenterOnScreen(self.filename,confidence=0.8,region=regionbox):
            return True
        else:
            return False

    @property
    def pos(self):
        # openCVを用いて範囲内に画像があるか調べる
        #文字認識も有効
        try:
            self.pos_x,self.pos_y = pg.locateCenterOnScreen(self.filename,confidence=0.8,region=regionbox)
        except:
            self.pos_x,self.pos_y = (None,None)
        #現在地によって機能を変える(未実装)
        return self.pos_x,self.pos_y

    @property
    def exist(self):
        return os.path.isfile(self.filename)

    @property
    def click(self):
        if self == Image_recognition('dummy'):
            pass
        else:
            time.sleep(random.uniform(0,0.2))
            self.pos_x,self.pos_y =  pg.locateCenterOnScreen(self.filename,confidence=0.8,region=regionbox)
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
        self.l = [[] for i in range(20)]
        self.l[0] = self.ok = Image_recognition("ok.png")
        self.l[1] = self.reload = Image_recognition("reload2.png")
        self.l[2] = self.bookmark = Image_recognition("bookmark_win.png")
        self.l[3] = self.quest_supporter = Image_recognition("quest_supporter_win.png")
        self.l[4] = self.raid_multi = Image_recognition("raid_multi_win.png")
        self.l[5] = self.raid = Image_recognition("raid_win.png")
        self.l[6] = self.result_multi = Image_recognition("result_multi_win.png")
        self.l[7] = self.result = Image_recognition("result_win.png")
        self.l[8] = self.quest_supporter = Image_recognition("result_multi_win.png")
        self.l[9] = self.quest_supporter = Image_recognition("result_multi_win.png")
        self.l[10] = self.attack = Image_recognition("attack2.png")
        self.l[11] = self.semi = Image_recognition("semi.png")
        self.l[12] = self.full = Image_recognition("full.png")
        self.l[13] = self.summon_choice = Image_recognition("summon_choice2.png")
        self.l[14] = self.attack_cancel = Image_recognition("attack_cancel.png")
        self.l[15] = self.summon_fin = Image_recognition("summon_fin.png")
        self.l[16] = self.verify1 = Image_recognition("verify1.png")
        self.l[17] = self.verify2 = Image_recognition("verify2.png")

        self.l[18] = self.summon_friend = Image_recognition(info['summon_friend'])
        self.l[19] = self.summon_battle = Image_recognition(info["summon_battle"])

        self.dummy = Image_recognition('dummy')
        self.prepare()

    """初期設定としてファイル損失やディレクトリパス指定ミス時にエラーを出す"""
    def prepare(self):
        for i in range(len(self.l)):
            if not self.l[i].exist:
                print("error occured while preparing images")
                print(self.l[i].filename+" does not exist.")
                sys.exit()


'''フローを実行するクラス
[todo][fin]ランダムで待機時間を設定したい
[todo]巡回を早くして、固まっているかの判断をしている間に高速巡回・クリックしたい'''
class BattleFlow(Read_img):

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
            #try:
            curlist[num].click
            print(curlist[num].filename+"clicked")
            time.sleep(duration[num])
            print("wait for "+str(duration[num])+"sec")
            if curlist[num+1].judge:
                print(curlist[num+1].filename+"was found")
                pass
            elif not curlist[num+1].judge:
                time.sleep(5)
                print(curlist[num+1].filename+"was not there. wait for 5 sec")
                if curlist[num+1].judge:
                    print(curlist[num+1].filename+"was found")
                    pass
                else: #リロード、ブックマーク
                    print("nothing was found. try again.")
                    self.if_move([self.reload,self.bookmark,url],url,[3,4],n-1)
                    return self.if_move(curlist,url,duration,n-1)
            #except:
                #self.if_move([self.reload,self.bookmark,url],url,[3,4],n-1)
                #return self.if_move(self,curlist,url,duration,n-1)


    """フレンド選択からバトルスタートのフロー"""
    @property
    def friend_phase(self):
        #フレンド石選択→ok
        self.if_move([self.summon_friend,self.ok],self.quest_supporter,[0.5],3)
        if pg.locateCenterOnScreen('verify1.png',grayscale=True,confidence=0.7,region=regionbox):
            sys.exit()
        elif pg.locateCenterOnScreen('verify2.png',grayscale=True,confidence=0.7,region=regionbox):
            sys.exit()
        self.if_move([self.ok,self.raid_multi],self.quest_supporter,[1],3)


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
        self.if_move(
        [self.dummy,self.attack],self.raid_multi,[7],3)
        self.if_move([self.summon_choice,self.summon_battle,self.ok,self.attack,self.semi],self.raid_multi,[0.5,0.5,0.5,3],3)
        self.if_move([self.reload,self.bookmark],self.result_multi,[3],3)
        self.if_move([self.bookmark,self.summon_friend],self.result_multi,[4],3)


    info = {
    'summon_friend':'summon_friend.png' ,
    'summon_battle':'rose.png',
    }

    #[todo]infoの辞書にリストを渡すと気軽に追加できるようなクラス作成

def test():

    #フレンド選択画面におけるフレンド召喚石の設定

    B.friend_phase
    print("friend_phase fin")
    B.attack_phase1
    print("attack_phase1 fin")
    #BattleFlow('summon_friend.png').battle

    """
    #理想
    click(varuna) #フレンド選択
    click(battlestart,info) #バトル開始～終了まで
    """

if __name__ == "__main__":

    B= BattleFlow(info)

    B.dummy.click
    print('fin')
