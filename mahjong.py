# -*- coding: utf-8 -*-
# Author: Frank-the-Obscure @ GitHub
# mahjong basic module

import re
import random
from evalScore import evalScore
from itertools import *
import Counter

#################################################
#           tranform to our card
#################################################
transform = { '5z':0, '6z':10, '7z':20,
                  '1m':1, '1s':11, '1p':21,
                  '2m':2, '2s':12, '2p':22,
                  '3m':3, '3s':13, '3p':23,
                  '4m':4, '4s':14, '4p':24,
                  '5m':5, '5s':15, '5p':25,
                  '6m':6, '6s':16, '6p':26,
                  '7m':7, '7s':17, '7p':27,
                  '8m':8, '8s':18, '8p':28,
                  '9m':9, '9s':19, '9p':29,
                  '1z':30, '3z':31, '2z':32, '4z':33
                  }

transform_rev = {     0:'5z', 10:'6z', 20:'7z',
                      1:'1m', 11:'1s', 21:'1p',
                      2:'2m', 12:'2s', 22:'2p',
                      3:'3m', 13:'3s', 23:'3p',
                      4:'4m', 14:'4s', 24:'4p',
                      5:'5m', 15:'5s', 25:'5p',
                      6:'6m', 16:'6s', 26:'6p',
                      7:'7m', 17:'7s', 27:'7p',
                      8:'8m', 18:'8s', 28:'8p',
                      9:'9m', 19:'9s', 29:'9p',
                      30:'1z', 31:'3z', 32:'2z', 33:'4z'
                  }
verbose = False

###############################################
###      他創建了一個class用來表示每"一"張牌      
###      rank是數字（rank型態是group的object）
###      suit是花色（suit型態是字串）
###      可以用str(card)來拿取。ex:'1m'
###############################################
class Card:
    """docstring for card"""
    def __init__(self, card):
        super(Card, self).__init__()
        self.suit = re.search('[mpsz]', card).group()
        if self.suit is 'z':
            self.rank = int(re.search('[1-7]', card).group())
        else:
            self.rank = int(re.search('[1-9]', card).group())       

    def __str__(self):
        return str(self.rank) + self.suit#ex:'1'+'m'

    def get_suit(self):
        return self.suit #'m','p','s','z'

    def get_rank(self):
        return self.rank #'1'or '2' or etc....'3456789'

    def get_flag(self):
        return self.flag

    def set_flag(self, flag):
        self.flag = flag
######################################################################################################################
#創建了一個class用來表示每組牌           
#不一定是已經組合好的牌
#牌組類型：
#1張 - 孤張："guzhang",ex:1m
#2張 - 兩張花色及數字一樣,對子:"duizi" 
#2張 - 差一張即可成為順子，不為字,ex:3m4m,兩面："liangmian" / 如果是12或89即為，邊張："bianzhang" 
#                          / 不連續的,ex:1m3m,坎張："kanzhang"  
#3張 - 3張一樣,刻子："kezi"
#    - 3張連續,順子："shunzi"
#    - 3張缺一，連坎："liankan" ex: 1m3m5m  
#    - 復合搭:"fuheda",# 复合搭共有112 113 122 133四种形态: 1 3张差别为1或2; 因排序第二张必然位于中间,且不是顺子(否则已经return)        
######################################################################################################################
#MIANZI = ['shunzi', 'kezi']  面子是指已經完成三張或4張的組合，包括順子和刻子（code裡並沒有考慮槓！）
#QUETOU = ['duizi'] 雀頭就等於對子
#DAZI = ['duizi'（對子）, 'bianzhang'（邊張）, 'kanzhang'（坎張）, 'liangmian'(兩面)] 搭子，一個面子的前身，一個已經組好的面子或是一個雀頭，
#GUZHANG = ['guzhang'] 孤張
######################################################################################################################
#可以用str(group)來拿取。ex:'1m2m'
######################################################################################################################
class Group(object):
    """docstring for Group
    手牌组: 面子 雀头 搭子 复合搭, etc.

    """
    def __init__(self, cards, closed=True):
        # cards: card 列表(in Card class)
        super(Group, self).__init__()
        self.cards = cards # 牌组成员列表, 使用列表表示
        self.closed = True # 是否都在手中(closed)
        self.type = self.cal_type()#將用來建立這個object的手牌去定義他的類型並存在type這個變數之中，這個變數是一個string

    def __str__(self): # note: 如何把列表串联变成字符最快, 似乎 py doc FAQ 有
        str_group = ''
        for card in self.cards:
            str_group += str(card)
        #print ("str_group",str_group)
        return str_group#ex:1m2m,3m3m3m

    def sort(self):
        if self.type in MIANZI:
            sort_type = 0
        elif self.type in QUETOU:#QUETOU:雀頭
            sort_type = 1
        elif self.type in DAZI: # todo 需要排序, 按照面子雀头搭子孤张顺序
            sort_type = 2
        elif self.type in GUZHANG:#GUZHANG：孤張
            sort_type = 3
        sort_suit = self.cards[0].get_suit()
        return str(sort_type) + sort_suit + str(self) 
        #类型+花色+内容; 如0m1m2m3m(面子 万 123m)1s3s3s

    def get_cards(self):
        return self.cards#cards:mahjong.card object

    def cal_type(self):
        """返回牌组类型: 面子 雀头 搭子 复合搭

        i: 排序的手牌(便于判断搭子大小顺序)
        p: 先根据张数归类, 再判断是否成牌组
        o: 1 孤张 2 雀头/两面/边张/坎张 3 刻子/顺子/连坎/复合搭(特指搭子加对子型)...
        """
        if len(self.cards) == 0:
            return None
        elif len(self.cards) == 1:
            return "guzhang"
        elif len(self.cards) == 2:
            if self.cards[0].get_suit() == self.cards[1].get_suit():
                if self.cards[0].get_rank() == self.cards[1].get_rank():#兩張花色及數字一樣,對子:"duizi"
                    return "duizi"
                elif (self.cards[0].get_rank() == self.cards[1].get_rank() - 1 and 
                      self.cards[0].get_suit() is not 'z'): #两面或边张
                    if self.cards[0].get_rank() == 1 or self.cards[0].get_rank() == 8: # 12, 89 边张
                        return "bianzhang"#ex:1m2m
                    else: #两面
                        return "liangmian"#ex:8m9m
                elif (self.cards[0].get_rank() == self.cards[1].get_rank() - 2 and 
                      self.cards[0].get_suit() is not 'z'): #坎张
                    return "kanzhang"#ex:1m3m
            else:
                return None
        elif len(self.cards) == 3:
            # todo: 每次都取回可能比较慢, 也许要考虑提取出来用变量暂存?
            if (self.cards[0].get_suit() == self.cards[1].get_suit() and 
                self.cards[0].get_suit() == self.cards[2].get_suit()):
                if (self.cards[0].get_rank() == self.cards[1].get_rank() and 
                    self.cards[0].get_rank() == self.cards[2].get_rank()):
                    return "kezi"#刻子
                    # todo: 可能要加入复合搭
                elif (self.cards[0].get_suit() is not 'z' and
                      self.cards[0].get_rank() == self.cards[1].get_rank() - 1 and 
                      self.cards[1].get_rank() == self.cards[2].get_rank() - 1): # 顺子不能是字牌
                    return "shunzi"
                elif (self.cards[0].get_suit() is not 'z' and
                      self.cards[0].get_rank() == self.cards[1].get_rank() - 2 and 
                      self.cards[1].get_rank() == self.cards[2].get_rank() - 2): # 顺子不能是字牌
                    return "liankan"
                elif (self.cards[0].get_suit() is not 'z' and
                      (self.cards[0].get_rank() == self.cards[2].get_rank() - 1 or 
                       self.cards[0].get_rank() == self.cards[2].get_rank() - 2)):
                    # 复合搭共有112 113 122 133四种形态: 1 3张差别为1或2; 因排序第二张必然位于中间,且不是顺子(否则已经return)
                    return "fuheda"
            else:
                return None
        else: 
            return None
    
    def get_type(self):#return是一個string，定義在上面那個cal_type中
        return self.type

    def youxiaopai(self, make=''):#這裡是Group這個class裡的有效牌function，下面還有一個XD不要搞錯了
        """返回有效牌类型(和数量?)

        i: 牌组
        o: 有效牌列表, in Card class
        """
        if self.type in MIANZI:
            return []#已經組好了不需要有效牌
        elif self.type is 'duizi':
            return [self.cards[0]]#對子還可以組成刻子，所以回傳一張有效牌
        elif self.type is 'bianzhang':#ex:1m2m or 8m9m00000000000000000000000000000000000000000000000000000000
            if self.cards[0].get_rank() == 1:#1m2m
                rank = '3'#代表他需要3
            else:
                rank = '7'
            return [Card(rank + self.cards[0].get_suit())]#ex:回傳3m
        elif self.type is 'kanzhang':#ex:1m3m
            rank = str(self.cards[0].get_rank() + 1)
            return [Card(rank + self.cards[0].get_suit())]#ex:回傳2m
        elif self.type is 'liangmian':#ex:3m4m
            rank1 = str(self.cards[0].get_rank() - 1)#2m
            rank2 = str(self.cards[0].get_rank() + 2)#5m
            return [Card(rank1 + self.cards[0].get_suit()),
                    Card(rank2 + self.cards[0].get_suit())]
        elif self.type is 'guzhang':#下面在計算整個手牌的有效牌的時候，會把孤張分為，為了做雀頭的牌，或是用來做搭子的牌
            if make is 'quetou' or self.cards[0].get_suit() is 'z': # 为了做雀头, 或字牌也只有本身
                return [self.cards[0]]
            else:#用來做搭子，ex:手上的牌為3m，會回傳1m,2m,3m(??),4m,5m
                ranks = [-2, -1, 0, 1, 2]
                return [Card(str(rank + self.cards[0].get_rank()) + self.cards[0].get_suit()) 
                        for rank in ranks 
                        if rank + self.cards[0].get_rank() in range(1, 10)]
        else:
            return []
   
        
######################################################################################
#這個class是用來計算手牌的有效牌。
#在之後的一個FUNCTION中，會將手牌整理為不同的牌組並創建成不同的hand_in_group，這樣就會得到不同種的胡牌牌型，以計算其有效牌。
#一個hand_in_group是一種組合（14張）。
######################################################################################
class Hand_in_group(object):
    """docstring for Hand_in_group

    i: groups列表, 如果不输入默认为空
    """
    def __init__(self, groups=[]):
        super(Hand_in_group, self).__init__()
        self.groups = groups[:] 
        # 如果不copy而是直接赋值, 会出现问题: 
        # 几个类变量使用同一个列表(和一开始以为的新建列表不同).
        # 虽然类变量地址不同, 但列表的链接相同!
    ###return的格式 ex: duizi-1p1p; duizi-5s5s; kanzhang-5m7m; kanzhang-3p5p; kanzhang-1s3s; guzhang-8m; guzhang-2p; guzhang-4z; 
    def __str__(self): # note: 如何把列表串联变成字符最快, 似乎 py doc FAQ 有
        str_hand = ''
        for group in self.groups:
            str_hand += group.get_type() + '-' + str(group) + '; '
        #print ("str_hand,",str_hand)
        return str_hand

    def append(self, new_group): #將新的GROUP加入
        self.groups.append(new_group)
        return self

    def remove(self, remove_group): #將指定的GROUP刪掉
        for group in self.groups:
            if is_samegroup(remove_group, group): # todo: 判断两个类变量内容是否相同, 有无更好方法
                self.groups.remove(group)
                return
    def ingroups(self,targetgroup):
        for group in self.groups:
            if is_samegroup(targetgroup,group):
                return True
        return False

    def get_groups(self): #得到手牌裡的這些GROUPS
        return self.groups

    def sort(self):#??
        #排序
        self.groups.sort(key=Group.sort)

    def xiangtingshu(self):
        #計算這個手牌中的某些組合的數量並計算向聽數
        #计算向听数 n=8-2*面子-1*雀头(<=11*搭子(<=4-面子)
        num_mianzi = 0
        num_quetou = 0
        num_dazi = 0
        single = 0###

        for group in self.groups:

            type_of_group = group.get_type() 

            if type_of_group in MIANZI:

                num_mianzi += 1

            elif type_of_group in QUETOU and num_quetou < 1:

                num_quetou += 1

            elif type_of_group in DAZI and num_dazi < 4 - num_mianzi: 

                num_dazi += 1
            else:###
                single += 1###
        handcardNum = 3*num_mianzi + 2*(num_quetou + num_dazi) + single###未攤開的手牌數
        num_mianzi += int((13-handcardNum)/3)###
        if num_mianzi + num_dazi == 5:###面子加塔子數最多為4
            num_dazi -= 1###

        return 8 - 2 * num_mianzi - num_quetou - num_dazi
    
    def youxiaopai(self):
        """输出有效牌

        i: 牌组
        p: 按照面子-雀头-搭子-孤张排序并统计数量后, 即可按顺序处理
        o: 有效牌列表(Card class list)
        """

        debug = False

        num_mianzi = 0
        num_quetou = 0
        num_dazi = 0
        num_guzhang = 0
        if debug:
            print ("-----------------------")
            print ('groups:')
        for group in self.groups: # 计算各个组成部分的数量
            if debug:
                print (str(group))
            type_of_group = group.get_type() 
            if type_of_group in MIANZI:
                num_mianzi += 1
            elif type_of_group in QUETOU:
                num_quetou += 1
            elif type_of_group in DAZI and num_dazi < 4 - num_mianzi: 
                num_dazi += 1
            else:
                num_guzhang += 1
        #print ()
        list_youxiaopai = [] # 用列表存放所有的有效牌
        #print ("-----------------------")
        for group in self.groups:
            #print ("group",str(group))
            type_of_group = group.get_type() 
            if type_of_group in MIANZI: # 面子没有有效牌
                pass
            elif (type_of_group is 'duizi' and 
                  num_quetou > 1 and num_mianzi < 4): 
                # 两个以上雀头, 且面子未完成时有对倒
                list_youxiaopai += group.youxiaopai()
                
            elif (type_of_group is 'duizi' and 
                  num_guzhang > 0 and num_mianzi + num_dazi < 4): 
                # 或搭子还不足, 任意孤张都是有效牌
                list_youxiaopai += group.youxiaopai()
            elif (type_of_group in ['bianzhang', 'kanzhang', 'liangmian'] and
                  num_mianzi < 4): 
                list_youxiaopai += group.youxiaopai()
            elif type_of_group is 'guzhang': # 孤张有两种情况, 形成搭子和形成雀头
                if num_quetou == 0:
                    list_youxiaopai += group.youxiaopai(make='quetou')
                elif num_mianzi + (num_quetou - 1) + num_dazi < 4: 
                # 面子+(对子-1)+搭子<4
                    list_youxiaopai += group.youxiaopai()
        if debug == True:
            for pair in groups_with_youxiaopai:
            
                print ('group and 有效牌 pairs : ', str(pair[0]),end=' ')
                for card in pair[1]:
                    print(str(card),end='')
                print ()   
       
        return list_youxiaopai
            
  

MIANZI = ['shunzi', 'kezi']
QUETOU = ['duizi']
DAZI = ['duizi', 'bianzhang', 'kanzhang', 'liangmian']
GUZHANG = ['guzhang'] # init respones

CARD_LIST = [str(rank) + suit 
             for suit in ['m', 'p', 's', 'z'] 
             for rank in range(1, 10) 
             if rank in range(1,8) or suit is not 'z']

CARD_LEFT = {card:4 for card in CARD_LIST} # 存储剩余牌量的字典, 通过 used_card 删除

VALID_LENGTH_OF_HAND = 14
MIANZI_MAX = 4
QUETOU_MAX = 1
XIANGTINGSHU_MAX = 8
finished_hand = [] # use this list for storing finished hand after iteration

def init_paishan():
    """ 生成136张牌山
    i: nothing
    o: a list of 136 random card
    """
    paishan_list = CARD_LIST * 4
    random.shuffle(paishan_list)
    return paishan_list

def used_card(card): # 从字典中去掉用过的牌, card in Card class
    CARD_LEFT[str(card)] -= 1

def is_samegroup(group1, group2):
    #判断两个牌组是否相同, 使用 str() 比较字符串
    return str(group1) == str(group2)

def is_samehandingroup(hand_in_group1, hand_in_group2):
    return str(hand_in_group1) == str(hand_in_group2) 

def print_hand(hand):
    """print hand for testing

    """
    for card in hand:
        print(card, end='')
    print()

def issamehand(hand1, hand2):
    """判断两手牌是否完全相同: 但需要先排好序再用
    """
    if len(hand1) != len(hand2):
        return False
    else:
        i = 0
        while i < len(hand1):
            if not is_samecard(hand1[i], hand2[i]):
                return False
            i += 1
        return True

def is_samecard(card1, card2):
    """判断两张牌是否相同
    """
    return str(card1) == str(card2)

def sort_Group(group):
    cards = group.get_cards()
    cards.sort(key=sort_hand)
    return Group(cards)

def Eval_WinPattern(xiangtingshu,totalcards_in_group,hand,cardsOnboard = Hand_in_group()):
    OPEN_CARDs = []
    # hand cards classification (after take card)
    TakeZero_CARDs = [] #original is MIANZI
    TakeOne_CARDs = []
    TakeTwo_CARDs = []
    # hand cards classification (after take card)
    Two =  []
    Three= []
    beforeAdd = Counter.Counter()# groups after add : groups before add

    #others : cannot form combination ,"liankan" "fuheda" 
    others = []

    debug =False
    if debug:
        print ("--------Eval WinPattern-----------")
        print("total cards:")
    num_quetou = 0
   
    for group in totalcards_in_group.get_groups():
        if group.get_type()=='duizi':
            num_quetou+=1
        if debug:
            print (str(group),end=',')
    #print ()
    # put opencards into OPEN_CARDs
    for group in cardsOnboard.get_groups():
        OPEN_CARDs.append(group)
    # add handcards youxiaopai, calculate their combinations
    # add these combinations into list for winpatterns calculation
    for group in hand.get_groups():
        type_of_group = group.get_type()
        if type_of_group in MIANZI:

            TakeZero_CARDs.append(group)#面子就不會有其他種組合
            Three.append(group)
            beforeAdd[group] = group

        elif type_of_group =='kanzhang' or type_of_group =='bianzhang':
            youxiaopai = group.youxiaopai()
            card = youxiaopai[0]
            #判斷還有沒有這張有效牌
            card_left = CARD_LEFT[str(card)]
            if card_left ==0:
                continue
            comb = Group(group.get_cards() + youxiaopai)
            comb = sort_Group(comb)
            TakeOne_CARDs.append(comb)
            Three.append(comb)
            beforeAdd[comb]=group
            
                
            assert len(youxiaopai)==1
        elif type_of_group == 'liangmian':
            youxiaopai = group.youxiaopai()
            for card in youxiaopai:
                card_left = CARD_LEFT[str(card)]
                if card_left ==0:
                    continue
                comb = Group(group.get_cards()+[card])
                comb = sort_Group(comb)
                TakeOne_CARDs.append(comb)
                Three.append(comb)
                beforeAdd[comb]=group
                    
        elif type_of_group == 'duizi':
            youxiaopai = group.youxiaopai()
            card = youxiaopai[0]#判斷還有沒有這張有效牌
            card_left = CARD_LEFT[str(card)]
            if card_left ==0:
                continue
            comb = Group(group.get_cards() + youxiaopai)
            #雀頭
            TakeZero_CARDs.append(group)
            Two.append(group)
            beforeAdd[group]=group
            #three
            TakeOne_CARDs.append(comb)
            Three.append(comb)
            beforeAdd[comb]=group
                
        elif type_of_group == 'guzhang':
            if num_quetou == 0:
                youxiaopai = group.youxiaopai(make='quetou')
                card = youxiaopai[0]#判斷還有沒有這張有效牌
                card_left = CARD_LEFT[str(card)]
                if card_left ==0:
                    continue
                comb = Group(group.get_cards()+youxiaopai)

                TakeOne_CARDs.append(comb)
                Two.append(comb)
                beforeAdd[comb]=group
                   
                   
            else:
                youxiaopai = group.youxiaopai()#[1m, 2m, 3m, 4m, 5m]
                card = group.get_cards()#'2m'                  
                comb0 = Group(card + card + card)#['2m','2m','2m']
                TakeTwo_CARDs.append(comb0)
                Three.append(comb0)
                beforeAdd[comb0]=group

                #[1m, '2m', 3m, 4m], [6m,7m,'8m',9m]
                tmpcombs = combinations(youxiaopai , 3 )
                for comb in tmpcombs:
                    if card in comb:
                        cardsadd = comb.remove(card)
                        card_left = [0,0]
                        for i,card in enumerate(cardsadd):
                            card_left[i] = CARD_LEFT[str(card)]
                        if 0 not in card_left:
                            #comb_list.append(Group(comb),cardsadd ,2)
                            comb = sort_Group(comb)
                            TakeTwo_CARDs.append(comb)
                            Three.append(comb)
                            beforeAdd[comb]=group
        else:
            others.append(group)
    #if others:
    #    value = simpleEval(totalcards_in_group,hand,cardsOnboard)

    # now we have the combinations
    if debug:
        print ("comb in Three")
        for comb in Three:
            print (str(comb),", comes from",beforeAdd[comb])
        print ()

        print ("comb in Two")
        for comb in Two:
            print (str(comb),", comes from",beforeAdd[comb])
        print ()




    MIANZI_needed = 4 - len(OPEN_CARDs)
    hand_MIANZICombs = combinations(Three,MIANZI_needed)#take group in Three to form a pattern

    winPatterns = []
    i=0
    for combs in hand_MIANZICombs:
        
        # judge whether the combination is legal 
        #(take cards numbers less/equal than xiangtingshu+1)
        #doesn't have two groups add from same cards
        numTake =0
        beforeAddList = []
        for group in combs:
            beforeAddList.append(beforeAdd[group])
            if group in TakeOne_CARDs:
                numTake += 1
            elif group in TakeTwo_CARDs:
                numTake += 2 
        
        for group in Two:
            #print ("---pattern----",i,"----")
            i +=1
            beforeAddList2 = beforeAddList[:]
            numTake2 = numTake
            repeatUse = False

            beforeAddList2.append(beforeAdd[group])

            if group in TakeOne_CARDs:        
                numTake2 += 1
            debug = False
            if debug:
                tmp = [str(cards) for cards in beforeAddList2]
                print ("before Add LIST",tmp)

            if not len(beforeAddList2)==len(set(beforeAddList2)):
                #print ("LALALALAL ,",len(beforeAddList2),",",len(set(beforeAddList2)))
                repeatUse=True
            if repeatUse or numTake2 > xiangtingshu+1:
                continue
            winPattern = []
            for cards in OPEN_CARDs:
                winPattern.append(cards)
            for cards in combs:
                #print ("hand's comb in three",str(cards))
                winPattern.append(cards)
            #print ("hand's comb in Two",str(group))
            winPattern.append(group)
            winPatterns.append(winPattern)
    valueList = []
    for pattern in winPatterns:
        Open = []
        Hidden = []

        for cards in pattern:
            if cards in OPEN_CARDs:
                Open.append(cards)
            else:
                Hidden.append(cards)
            #print (str(cards),end=',')

        value = evalScore(groupsTransform(pattern),groupsTransform(Hidden),groupsTransform(Open))
        valueList.append( value )
        #print ('value= ' ,value )
        #print ()
    #print ("valueList",valueList)
    finalvalue = sum(valueList)/len(valueList)
    return finalvalue



            
def groupsTransform(ListOf_Groups):
    totallist = []
    for group in ListOf_Groups:
        comb = []#也就是一個group
        for card in group.get_cards():
            comb.append(transform[str(card)])
        totallist.append(comb)
    return totallist
def simpleEval(totalcards_in_group,hand,cardsOnboard=Hand_in_group()):
    """只將現在的手牌放入    
    放入格式：[[1,2,3],[4,5,6],[8,8],[9,9]]
    """
    # transform to our expression
    # totallist , handcards,boardcards
    totallist = []
    for group in totalcards_in_group.get_groups():
        comb = []#也就是一個group
        for card in group.get_cards():
            comb.append(transform[str(card)])
        totallist.append(comb)
    handcards = []
    for group in hand.get_groups():
        comb = []
        for card in group.get_cards():
            comb.append(transform[str(card)])
        handcards.append(comb)
    boardcards =[]
    for group in cardsOnboard.get_groups():
        comb = []
        for card in group.get_cards():
            comb.append(transform[str(card)])
        boardcards.append(comb)    

    value = evalScore(totallist,handcards,boardcards)
    
    return value
def hand_processer(hand, raw_hand=True, length=VALID_LENGTH_OF_HAND, check_input=False):
    """ process raw hand to single card list

    i: raw hand, length of hand, check input or not
    o: list of cards by Card class; 
    return None when wrong input & check input is True
    """
    if not raw_hand:
        hand.sort(key=sort_hand)
        return hand
    # or input raw_hand
    processed_hand = []
    # 1. separate hand
    for split in re.findall('[1-9]+[mpsz]', hand): 
        #valid number 1-9, valid suit mpsz
        suit = re.search('[mpsz]', split).group()
        ranks = re.findall('[1-9]', split)
        for rank in ranks:
            processed_hand.append(rank + suit)
    # 3. check if hand length is valid
    if len(processed_hand) != length and check_input:
        #print('hand is not valid, please check')
        return None
    # 4. output by Card class
    hand_in_class = [Card(card) for card in processed_hand]
    # 2. sort first by suit, second by rank
    hand_in_class.sort(key=sort_hand)
    return hand_in_class

def sort_hand(card):
    """ reverse hand name to sort by suit first

    i: list of card class
    """
    return card.get_suit(), card.get_rank()


###
#這是一個recursive function，從第一張手牌開始依次迭帶
#最花時間的就是在這裡！
def hand_to_group(hand_todo, hand_set=Hand_in_group()):
    """把手牌整理为不同的牌组并计算向听数

    i: hand set 使用分类 hand_todo: Card的列表; hand_set: Hand_in_group class
    p: 每张牌迭代, 尝试加入每一个牌组之中. 或作为孤张(速度慢的主要原因, 大约 2^n 复杂度)
    o: 列表, 每个成员是 tuple (向听数, 牌组列表)
    """
    global list_xiangtingshu, xiangtingshu_lowest

    debug = False
    if len(hand_todo) == 0: #finished（每個group都分好了）
        # 计算向听数, 如果小于等于当前最小值, 添加到列表中
        # todo: 速度优化. 直接先算一下len(), 如果len很大, 可不用排序直接return, 节约时间
        hand_set.sort()
        xiangtingshu = hand_set.xiangtingshu()
        if xiangtingshu == xiangtingshu_lowest:
            list_xiangtingshu.append((xiangtingshu, hand_set))
        elif xiangtingshu < xiangtingshu_lowest:
            xiangtingshu_lowest = xiangtingshu
            list_xiangtingshu = []
            list_xiangtingshu.append((xiangtingshu, hand_set))
        return

    card_to_set = hand_todo[0] # 需要处理的牌,第一次hand_todo[0]是手牌中的第一張
    #print()
    #print('card to process', card_to_set)
    ''' 
    print('groups now')
    for group in hand_set.get_groups():
        print (str(group),',',end='')
    '''
    #檢驗每個group（之前已經放入hand_set的）看可否組成新的，
    #如果可以的話就將原本的group remove掉，並將剩餘的手牌與新的groups放入遞迴。
    #如果不行的話就跳過這個group去執行下一個
    for group in hand_set.get_groups():
        type_group = group.get_type()
        group_plus_card = Group(group.get_cards() + [card_to_set])
        type_plus_card = group_plus_card.get_type()
        #print(type_of_cards(setted), hand_todo[0])# 

        if type_group in MIANZI: 
            # 如果已是面子, 无法添加, 则与孤张处理一样
            pass
        elif type_group in DAZI and type_plus_card in MIANZI:
            # 如果是搭子, 并可与新牌组成面子
            #print('make mianzi')
            hand_set_new = Hand_in_group(hand_set.get_groups())
            hand_set_new.remove(group)
            hand_set_new.append(group_plus_card)
            hand_to_group(hand_todo[1:], hand_set_new)
        elif type_group in GUZHANG and type_plus_card in DAZI:
            # 如果是孤张, 并可与新牌组成搭子
            #print('make dazi')#
            groups = hand_set.get_groups()
            new = Hand_in_group(groups)
            new.remove(group)
            new.append(group_plus_card)
            hand_to_group(hand_todo[1:], new)
    #第一次沒有groups時會走到這裡
    #finish之後也會走到這裡，然後hand_to_group就return空  
    hand_set_new = Hand_in_group(hand_set.get_groups())
    hand_set_new.append(Group([card_to_set]))
    hand_to_group(hand_todo[1:], hand_set_new)# 一張張处理

def cal_xiangtingshu(hand, cardsOnboard,raw_hand=True, output_notes=False):
    """计算向听数的封装

    i: hand set 使用分类 hand_todo: Card的列表, 最好是13张
    p: 先用hand_to_group分类; 去重; 合并不同 group 的所有有效牌; 输出
    o: 最小向听数, 有效牌数量, 有效牌列表
    """
    global list_xiangtingshu, xiangtingshu_lowest 
    #todo: 迭代无法传递, 故暂时使用了全局变量
    
    debug = False    
    verbose = False
    list_xiangtingshu = []
    xiangtingshu_lowest = XIANGTINGSHU_MAX #init

    hand = hand_processer(hand, raw_hand)
    if verbose:
        print("---------處理成為手牌組------------------------")
    hand_to_group(hand) # 1.处理成为手牌组
    if verbose:
        print("---------得到丟這張牌時最小的向聽數的牌組----------")
        print('向听数:', xiangtingshu_lowest) #
    unique_hands = []#---------得到最小的向聽數的牌組（去掉重複的）----------
    for num, hand in list_xiangtingshu: # 去重 #list_xiangtingshu是一個tuple(向聽數,hand_set)
        for unique_hand in unique_hands:
            if is_samehandingroup(hand, unique_hand):#是用hand_to_group object中的__str__做比較
                break
            elif cardsOnboard:# if this handset doesn't have group in boardgroup  ,去掉
                boardgroups = cardsOnboard.get_groups()
                b=False
                for group in boardgroups:
                    if not unique_hand.ingroups(group):
                        if verbose:
                            print (str(group),"not in ",str(unique_hand))
                        b = True

                if b:
                    break
        else:
            unique_hands.append(hand)
    debug = False

                  
    debug = False
    #print ()           
    unique_youxiaopais = []
    if verbose:

        print("---------得到丟這張牌時最小的向聽數的牌組的有效牌----------") 
    for hand in unique_hands: # 输出最小向听数的牌型
        #print(hand)
        for card in hand.youxiaopai():
            for youxiaopai in unique_youxiaopais:
                if is_samecard(card, youxiaopai):
                    break
            else: # todo 查阅 for else
                unique_youxiaopais.append(card)
    unique_youxiaopais.sort(key=sort_hand) # 排序, 稍作整理

    num_youxiaopai = 0
    for card in unique_youxiaopais:
        num_youxiaopai += CARD_LEFT[str(card)]

    if output_notes:
        for card in unique_youxiaopais:
            print(card, end = '')
        print()
    return xiangtingshu_lowest, num_youxiaopai, unique_youxiaopais , unique_hands



def xiangtingshu_output( hand , cardsOnboard,evaluate = False,raw_hand=True):
    """通过比较向听数和有效牌, 输出打某张, 向听数, 有效牌列表等何切信息

    i: hand 最好是14张
    p: 调用 cal_xiangtingshu(), 输出所有的可能最小向听数组合, 暂只支持标准型
    o: 输出何切信息
    """
    verbose = False
    hand = hand_processer(hand, raw_hand)#將input的凌亂的手牌排序並整理成他定義的class
    # todo: 只判断 unique card, 在重复型将可明显减少判断时间.
    cardsOnboardList = []
    if cardsOnboard:#([['1m','2m','3m'],['5m','6m','7m']]
        #將明牌整理成他們的group的型態
        
        boardCards_in_group = Hand_in_group()
        for group in cardsOnboard:
            groupcards=[]
            for card in group:
                
                cardnow = Card(card)
                cardsOnboardList.append(cardnow)
                used_card(cardnow)
                groupcards.append(cardnow)#[Card(1m),Card(2m),Card(3m)]

            groupT = Group(groupcards)#        
            boardCards_in_group.append(groupT)
        cardsOnboard = boardCards_in_group#已經整理成Hand_in_group 的格式
    xiangtingshu_lowest = 8 
    best_cards = []
    for card in hand: 
        used_card(card)# 將手牌從牌山中去掉，碰到一個牌就將那個牌的數量-1
    # done : 再這裡引入card open和cardsonboard，transfrom成他的class，並用used_card刪掉用過的牌

    # 统计出最小向听数
    card0 = ''
    for card in hand: 
        if is_samecard(card, card0):
            continue
        elif cardsOnboard:
            if card in cardsOnboardList:
                print ('cards on board',cardsOnboardList)
                continue # can't throw card on board
        else:
            if verbose:
                print ('throwing card is', card)
            card0 = card#從手牌中選出來，要被丟掉的那張牌。
        hand_card = hand[:]# card list
        hand_card.remove(card)
        total_card = hand_card + cardsOnboardList         
        #將某張牌丟掉之後，去計算向聽數
        xiangtingshu, num_youxiaopai, list_youxiaopai, hands_in_group = cal_xiangtingshu(total_card, cardsOnboard,raw_hand=False) 

        #input()
        if xiangtingshu < xiangtingshu_lowest:
            best_cards = [(card, xiangtingshu, num_youxiaopai, list_youxiaopai , hands_in_group)]
            xiangtingshu_lowest = xiangtingshu
        elif xiangtingshu == xiangtingshu_lowest:
            best_cards.append((card, xiangtingshu, num_youxiaopai, list_youxiaopai , hands_in_group))
    # 输出
    if verbose:
        print('手牌: ', end = '')
        print_hand(hand) # 输出手牌内容
        #print(best_cards)
        print("---------得到丟所有牌之後，最小的向聽數時的有效牌，及這些牌組的手牌牌型----------") 
    value_list=[]
    for card, xiangtingshu, num_youxiaopai, list_youxiaopai ,hands_in_group in best_cards:
        youxiaopai = ''
        for i in list_youxiaopai:
            youxiaopai += str(i)
        
        if  xiangtingshu<=3 and evaluate:
            #EVALUATION
            value = []  
            for hand in hands_in_group:
                
                if verbose:
                    print('hand in group : ', str(hand))

                if cardsOnboard:#翻開的牌，已經整理成Hand_in_group，因eval要算分數應該要所有的一起
                    totalcards_in_group = Hand_in_group(cardsOnboard.get_groups()+hand.get_groups())
                else:
                    totalcards_in_group = Hand_in_group(hand.get_groups())
                #print('evaluation winpattern....')
                #print ('simple eval ( evaluate only cards now)...')
                if cardsOnboard:
                    #value.append( simpleEval(totalcards_in_group,hand,cardsOnboard) )
                    value.append(Eval_WinPattern(xiangtingshu,totalcards_in_group,hand,cardsOnboard))
                else:
                    #value.append( simpleEval(totalcards_in_group,hand) )
                    value.append(Eval_WinPattern(xiangtingshu,totalcards_in_group,hand))
            totalvalue = sum(value)/len(value) #sumation of all 這些牌組的手牌牌型's value 
            #EVALUATION END
            value_list.append(totalvalue)# USE FOR RETURN, ONE THROW CARD ONE VALUE
            verbose = True
            if verbose:
                print('打{}, 向听数{}, 有效牌{}, {}种{}张, eval ={}'.format(card, xiangtingshu, youxiaopai, len(list_youxiaopai), num_youxiaopai,totalvalue))
        else:
            verbose = True
            if verbose:
                print('打{}, 向听数{}, 有效牌{}, {}种{}张'.format(card, xiangtingshu, youxiaopai, len(list_youxiaopai), num_youxiaopai))

        
    #my code
    xiangtingshuInfo = []
    for card, xiangtingshu, num_youxiaopai, list_youxiaopai , hand_in_group in best_cards:
    
        cardMapping = transform[str(card)]
        youxiaopaiMapping = []
        for i in list_youxiaopai:
            youxiaopaiMapping.append(transform[str(i)])
        xiangtingshuInfo.append([cardMapping, xiangtingshu, youxiaopaiMapping])
    if evaluate:
        return xiangtingshuInfo,value_list
    else:
        return xiangtingshuInfo,[]

    
def main():
    """main func.

    i: argv or input later
    o: is mahjong or not
    """
    from sys import argv
    try:
        script, input_hand = argv
    except ValueError:
        input_hand = input('input hand: ')

    xiangtingshu_output( input_hand, [ ['3m','4m','5m'] , ['1p','2p','3p'] ] )

if __name__ == '__main__':
    main()
