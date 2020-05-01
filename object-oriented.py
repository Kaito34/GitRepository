# encoding: utf_8

import pyautogui as pg
import os
import sys
import random
import time
import pygame.mixer
import cv2

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
regionbox = (0,50,1000,1500)
regionbox_hell = (1100,50,1400,1500)

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
        self.size

    @property
    def size(self):
        try:
            self.img = cv2.imread(self.filename,cv2.IMREAD_COLOR)
            self.height, self.width, self.channels = self.img.shape[:3]
        except:
            self.height, self.width, self.channels = None,None,None
        return self.height, self.width

    @property
    def judge(self):
        if pg.locateCenterOnScreen(self.filename,grayscale=True,confidence=0.8,region=regionbox):
            return True
        else:
            return False

    @property
    def strict_judge(self):
        if pg.locateCenterOnScreen(self.filename,grayscale=True,confidence=0.9,region=regionbox):
            return True
        else:
            return False

    @property
    def judge_for_hell(self):
        if pg.locateCenterOnScreen(self.filename,grayscale=True,confidence=0.8,region=regionbox_hell):
            return True
        else:
            return False

    @property
    def pos(self):
        # openCVを用いて範囲内に画像があるか調べる
        #文字認識も有効
        try:
            self.pos_x,self.pos_y = pg.locateCenterOnScreen(self.filename,grayscale=True,confidence=0.8,region=regionbox)
        except:
            self.pos_x,self.pos_y = (None,None)
        #現在地によって機能を変える(未実装)
        return self.pos_x,self.pos_y

    @property
    def loose_pos(self):
        # openCVを用いて範囲内に画像があるか調べる
        #文字認識も有効
        try:
            self.pos_x,self.pos_y = pg.locateCenterOnScreen(self.filename,grayscale=True,confidence=0.5,region=regionbox)
        except:
            self.pos_x,self.pos_y = (None,None)
        #現在地によって機能を変える(未実装)
        return self.pos_x,self.pos_y

    @property
    def pos_for_hell(self):
        try:
            self.pos_x,self.pos_y = pg.locateCenterOnScreen(self.filename,grayscale=True,confidence=0.8,region=regionbox_hell)
        except:
            self.pos_x,self.pos_y = (None,None)
        return self.pos_x,self.pos_y

    @property
    def exist(self):
        return os.path.isfile(self.filename)

    #[todo] クリックをブラす
    #[todo] 無駄なところをダミークリックする
    @property
    def click(self):
        if self.filename =='dummy':
            print("pass the click action")
            pass
        else:
            time.sleep(random.uniform(0,0.2))
            self.pos_x,self.pos_y =  pg.locateCenterOnScreen(self.filename,grayscale=True,confidence=0.8,region=regionbox)
            self.height, self.width = self.size
            self.pos_x_ran = random.uniform(self.pos_x-self.width/2+5,self.pos_x+self.width/2-5)
            self.pos_y_ran = random.uniform(self.pos_y-self.height/2+5,self.pos_y+self.height/2-5)
            pg.click(self.pos_x_ran,self.pos_y_ran)

    @property
    def click_for_hell(self):
        time.sleep(random.uniform(0,0.2))
        self.pos_x,self.pos_y =  pg.locateCenterOnScreen(self.filename,grayscale=True,confidence=0.8,region=regionbox_hell)
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
        self.l = [[] for i in range(25)]
        self.l[0] = self.ok = Image_recognition("ok.png")
        self.l[1] = self.reload = Image_recognition("reload2.png")
        self.l[2] = self.bookmark = Image_recognition("bookmark_win.png")
        self.l[3] = self.quest_supporter = Image_recognition("quest_supporter_win.png")
        self.l[4] = self.raid_multi = Image_recognition("raid_multi_win.png")
        self.l[5] = self.raid = Image_recognition("raid_win.png")
        self.l[6] = self.result_multi = Image_recognition("result_multi_win.png")
        self.l[7] = self.result = Image_recognition("result_win.png")
        self.l[8] = self.quest_supporter = Image_recognition("quest_supporter_win.png")
        self.l[9] = self.quest_supporter = Image_recognition("quest_supporter_win.png")
        self.l[10] = self.attack = Image_recognition("attack2.png")
        self.l[11] = self.semi = Image_recognition("semi.png")
        self.l[12] = self.full = Image_recognition("full.png")
        self.l[13] = self.summon_choice = Image_recognition("summon_choice2.png")
        self.l[14] = self.attack_cancel = Image_recognition("attack_cancel.png")
        self.l[15] = self.summon_fin = Image_recognition("summon_fin.png")
        self.l[16] = self.verify1 = Image_recognition("verify1.png")
        self.l[17] = self.verify2 = Image_recognition("verify2.png")
        self.l[18] = self.hell = Image_recognition("hell_check.png")
        self.l[18] = self.claim_loot = Image_recognition("claim_loot.png")
        self.l[19] = self.summon_row = Image_recognition("summon_row.png")
        self.l[20] = self.quest = Image_recognition("quest_win.png")

        self.l[21] = self.event_url = Image_recognition(info["event_url"])
        self.l[22] = self.summon_friend = Image_recognition(info['summon_friend'])
        self.l[23] = self.summon_battle = Image_recognition(info["summon_battle"])

        self.l[24] = self.auto = Image_recognition("auto.png")

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

    """固まった時の対処 for hell"""
    def if_move_for_hell(self,curlist,url,duration,n):

        print("n"+str(n)+"回目")
        if n == 0:
            sys.exit()

        for num in range(len(curlist)-1):
            #try:
            curlist[num].click_for_hell
            print(curlist[num].filename+"clicked")
            time.sleep(duration[num])
            print("wait for "+str(duration[num])+"sec")
            if curlist[num+1].judge_for_hell:
                print(curlist[num+1].filename+"was found")
                pass
            elif not curlist[num+1].judge_for_hell:
                time.sleep(5)
                print(curlist[num+1].filename+"was not there. wait for 5 sec")
                if curlist[num+1].judge_for_hell:
                    print(curlist[num+1].filename+"was found")
                    pass
                else: #リロード、ブックマーク
                    print("nothing was found. try again.")
                    self.if_move_for_hell([self.reload,self.bookmark,url],url,[3,4],n-1)
                    return self.if_move_for_hell(curlist,url,duration,n-1)
            #except:
                #self.if_move([self.reload,self.bookmark,url],url,[3,4],n-1)
                #return self.if_move(self,curlist,url,duration,n-1)

    """画像が出るまで待機するメソッド"""
    def wait_end(self,fileobj,sec):
        self.counter=0
        print("wait till this battle ends")
        while True:
            self.counter+=1
            if fileobj.judge:
                print("battle ends")
                break
            elif self.counter>100:
                break
            else:
                time.sleep(sec)


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

    @property
    #for solo
    def friend_phase1(self):
        #フレンド石選択→ok
        self.if_move([self.summon_friend,self.ok],self.quest_supporter,[0.5],3)
        if pg.locateCenterOnScreen('verify1.png',grayscale=True,confidence=0.7,region=regionbox):
            sys.exit()
        elif pg.locateCenterOnScreen('verify2.png',grayscale=True,confidence=0.7,region=regionbox):
            sys.exit()
        self.if_move([self.ok,self.quest],self.quest_supporter,[1],3)

    @property
    #for solo without ok button
    def friend_phase1(self):
        #フレンド石選択→ok
        self.if_move([self.summon_friend,self.ok],self.quest_supporter,[0.5],3)
        if pg.locateCenterOnScreen('verify1.png',grayscale=True,confidence=0.7,region=regionbox):
            sys.exit()
        elif pg.locateCenterOnScreen('verify2.png',grayscale=True,confidence=0.7,region=regionbox):
            sys.exit()
        self.if_move([self.ok,self.raid],self.quest_supporter,[1],3)



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

    @property
    #AT用
    def attack_phase2(self):
        self.if_move(
        [self.dummy,self.attack],self.raid_multi,[7],3)
        self.if_move([self.attack,self.semi],self.raid_multi,[3],3)
        self.if_move([self.reload,self.bookmark],self.result_multi,[3],3)
        self.if_move([self.bookmark,self.summon_friend],self.result_multi,[4],3)

    @property
    #Halo
    def attack_phase3(self):
        self.if_move(
        [self.dummy,self.attack],self.raid,[7],3)
        self.if_move([self.attack,self.semi],self.raid,[3],3)
        time.sleep(random.uniform(30,50)) #wait_till関数をつくる
        self.if_move([self.bookmark,self.summon_friend],self.result,[4],3)

    @property
    #Items with ok
    def attack_phase4(self):
        self.wait_end(self.ok,1)
        self.if_move(
        [self.ok,self.quest],self.raid,[0],3)
        while True:
            self.wait_end(self.auto,0.1)
            self.if_move([self.auto,self.raid],self.raid,[3],3)
            if self.raid.judge:
                break
        self.wait_end(self.result,3) #wait_till関数をつくる
        self.if_move([self.bookmark,self.summon_friend],self.quest_supporter,[4],3)

    @property
    #Items
    def attack_phase5(self):
        while True:
            self.wait_end(self.auto,0.1)
            self.if_move([self.auto,self.raid],self.raid,[3],3)
            if self.raid.judge:
                break
        self.wait_end(self.result,3) #wait_till関数をつくる
        self.if_move([self.bookmark,self.summon_friend],self.quest_supporter,[4],3)

    """hellをスキップできるかをチェックする"""
    @property
    def hell_check(self):
        self.if_move_for_hell([self.reload,self.event_url],self.event_url,[5],3)
        if self.hell.judge_for_hell:
            self.if_move_for_hell([self.hell,self.claim_loot,self.reload,self.event_url],self.reload,[2,3,3],3)
        else:
            pass

    """hellをスキップできるかをチェックする"""
    @property
    def hell_check_halo(self):
        self.if_move_for_hell([self.reload,self.event_url],self.event_url,[5],3)
        if self.hell.judge_for_hell:
            pygame.mixer.init()
            pygame.mixer.music.load("info-girl1-syuuryou1.mp3")
            pygame.mixer.music.play(1)
        else:
            pass

    @property
    def verify(self):
        pygame.mixer.init()
        pygame.mixer.music.load("info-girl1-syuuryou1.mp3")
        if self.verify1.judge:
            pygame.mixer.music.play(1)
            sys.exit()
        elif self.verify2.judge:
            pygame.mixer.music.play(1)
            sys.exit()
        elif not self.summon_row.judge:
            pygame.mixer.music.play(1)
            sys.exit()
        else:
            pass

#[todo]infoの辞書にリストを渡すと気軽に追加できるようなクラス作成
#[todo]AP回復のフロー
#[todo]時間待機指定をwait_endで置き換え

#global
info = {
'event_url':'event_url.png' ,
'summon_friend':'summon_friend.png' ,
'summon_battle':'rose.png',
}

B= BattleFlow(info)

def test(num):
    for i in range(num):
        print(str(i)+"回目のバトルです")

        #ツール対策
        B.verify

        #フレンド選択画面におけるフレンド召喚石の設定
        B.friend_phase1
        print("friend_phase1 fin")
        B.attack_phase5
        print("attack_phase fin")


        """
        if i%random.uniform(1,10) == 0:
            B.hell_check
        elif i%10 == 0:
            B.hell_check
        else:
            pass
        """

        time.sleep(random.uniform(0,5))

        """
        #理想
        click(varuna) #フレンド選択
        click(battlestart,info) #バトル開始～終了まで
        """
"""
#stuck over flow
bookmark_win.pngwas found
bookmark_win.pngclicked
wait for 4sec
result_multi_win.pngwas not there. wait for 5 sec
"""

if __name__ == "__main__":
    try:
        test(10)
    except:
        pygame.mixer.init()
        pygame.mixer.music.load("Vikala.mp3")
        pygame.mixer.music.play(1)

    pygame.mixer.init()
    pygame.mixer.music.load("info-girl1-syuuryou1.mp3")
    pygame.mixer.music.play(1)
