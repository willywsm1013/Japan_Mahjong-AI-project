#-*- coding: utf-8 -*-　
###################################################################################
###    evalScore(所有牌的組合（明+暗），暗牌組合,明牌組合，贏的Agent =None(可以贏了再指定）,贏的Agent的門風=None,胡牌的時機)
###    可以丟入可胡牌的牌型及還不能胡牌的牌型去估計其分數
###    有些判斷要真的胡牌才能判斷，那我就不會把這個分數加進估計值
###    Ex: 
###    winCards = [[13, 14, 15], [25, 25], [30, 30, 30, 30], [14, 15, 16], [22, 23, 24]]
###    hiddenCards = [[13, 14, 15], [25, 25]]
###    openCards = [[30, 30, 30, 30], [14, 15, 16], [22, 23, 24]]
###    winTime = '天胡'
###    getScore(winCards, hiddenCards , openCards )
###################################################################################
from BasicDefinition import CardIndex
def evalScore( totalCards, hiddenCards , openCards ,winagent = None, agentWind = None , winTime = None ,verbose=False,output_Han = False):    
                
    paircards = []  # '雀'
    fourOfAKind = [] # '槓'
    threeOfAKind = [] # '碰'(刻)
    straight = [] #　'吃'
        
    win = False #代表這個牌形是可以胡牌的牌型
   
    others =[]
    
    winCards = totalCards

    winCard =[] #no combination , easy for calculation,means total card
    #print ("The cards ", listDict(winCards,2))
    verbose = False

    if verbose:
        if win:
            print ("Agent" , winAgent , "Win!!")
        #print ("The cards win is : ", winCards )
        print ("The cards win is : ", listDict(winCards,2))
        print ( "Among them, hidden is ",hiddenCards , "; Opened is ,",openCards)
        print ("----------------------------------------")   

    verbose = False 
    for cards in winCards:
        for card in cards:
            winCard.append(card)
    #將牌的組合對類型做分類

    for comb in winCards:
       
        
        if getKinds(comb)=='雀': 
           paircards.append(tuple(comb))
        elif getKinds(comb)=='槓':
           fourOfAKind.append(tuple(comb))
        elif getKinds(comb)=='碰':
           threeOfAKind.append(tuple(comb))
        elif getKinds(comb)=='吃':
           straight.append(tuple(comb))
        else:
           others.append(tuple(comb))
        
    if verbose:
        
           print ("順 ",straight)
           print ("碰 ",threeOfAKind)
           print("槓 ",fourOfAKind)
           print ("雀",paircards)
           print ("----------------------------------------")    
    if (len(straight)+len(threeOfAKind) + len(fourOfAKind)) ==4 and len(paircards)==1:
        win = True
    if verbose:
        print ("win or not : ",win)
    m = []    #萬條餅字
    l = []
    p = []
    z = []
    for cards in winCards:
        for card in cards:
            if 1 <= card <= 9:
                m.append(card)
            elif 11 <= card <=19:
                l.append(card)
            elif 21 <= card <= 29:
                p.append(card)
            else:
                z.append(card)
    s=[m,l,p,z]
        
    if verbose:
        print ("card classfied in colors : ")
        print (s)
        print ('[',end='')
        for color in s:
            print ('[ ',end='')
            for card in color:
                print (CardIndex[card],end=',')
            print ('\b],',end='')
        print (']')           
        print ("----------------------------------------")      
                
    score = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    output_Hanname = []
    ###  0-雜項  ###
        
    if len(straight)==4:
        output_Hanname.append("平和（平胡)\t|\t(1番/5分)")
        #print ("平和（平胡)\t|\t(1番/5分)")
        score[0] = score[0]+5
    elif not openCards:
        output_Hanname.append("門前清\t|\t(1番/5分)")
        score[0] = score[0]+5
    else:
        matches = [x for x in winCard if (x%10)==1 or (x%10==9) or (x%10)==0 or (x<=41 and x>=30)]
        if not matches:
            output_Hanname.append("斷么九\t|\t(1番/5分)")#沒有1、9和字牌
            score[0] = score[0]+5
      
    ###  1-清一色類  ###

    matches = [color for color in s if len(color)==len(winCard)] 
    if matches:
          output_Hanname.append("清一色\t|\t(10番/80分)")
          score[1]=score[1]+80
    else:
       matches = [color for color in s if color!=z and len(color)==(len(winCard)-len(z))]
       if matches and len(z)!=0:
          output_Hanname.append("混一色\t|\t(3番/40分)")
          score[1]=score[1]+40
     
    #九子連環　需清一色　門前清且　手牌為　[１１１２３４５６７８９９９] 加上1~9任一張　
    
    ###  2字牌類  ###　

    matchesThree = [ pair for pair in threeOfAKind if pair[0]%10==0 and pair[0]!=30 ] # match中發白
    matchesFour = [pair for pair in fourOfAKind if pair[0]%10==0 and pair[0]!=30] #match中發白的槓
    matchesThreeWind = [ pair for pair in threeOfAKind if pair[0]<=33 and pair[0]>=30 ] #match東南西北
    matchesFourWind = [ pair for pair in fourOfAKind if pair[0]<=33 and pair[0]>=30 ]  #match東南西北的槓

    #2.1番牌：有中發白的刻子/槓及該玩家其門風的刻子，每個１０分　（暫不計門風）
    if matchesThree or matchesFour:
        score[2] = score[2] + 10*(len(matchesThree)+len(matchesFour))
        output_Hanname.append("三元牌\t|\t(1番/10分)")            
    #2.2.1 小三元：有中發白的刻子/槓兩個及一個中發白的雀子
    if (len(matchesThree)+len(matchesFour))==2 and paircards and paircards[0][0]%10==0 and paircards[0][0]!=30:
        output_Hanname.append("小三元\t|\t(5番/40分)")
        score[2] = score[2] + 40
        
    #2.2.2 大三元
    elif (len(matchesThree)+len(matchesFour))==3:
        output_Hanname.append("大三元\t|\t(10番/130分)")
        score[2] = score[2] + 130
      
    #2.3 風牌 東南西北[30,31,32,33]

    #2.4 三風類
    if (len(matchesThreeWind)+len(matchesFourWind))==2 and paircards and (paircards[0][0]<=33 and paircards[0][0]>=30):
        output_Hanname.append("小三風\t|\t(X番/30分)")
        score[2] = score[2] + 30
    elif (len(matchesThreeWind)+len(matchesFourWind))==3:
        if paircards and paircards[0][0]<=33 and paircards[0][0]>=30:
            output_Hanname.append("小四喜\t|\t(20番/320分)")
            score[2] = score[2] + 320
        else:
            output_Hanname.append("大三風\t|\t(X番/120分)")
            score[2] = score[2] + 120
    elif (len(matchesThreeWind)+len(matchesFourWind))==4:
        output_Hanname.append("大四喜\t|\t(10番/400分)")
        score[2] = score[2] + 400

    # 2.5 字一色
    matches = [color for color in s if len(color)==len(winCard)] 
    if matches and z and matches[0]==z:
          output_Hanname.append("字一色\t|\t(10番/320分)")
          score[2] = score[2]+320
    
    ###   3   ###

    # 3.1 對對和    
    if (len(threeOfAKind)+len(fourOfAKind))==4:
        output_Hanname.append("對對和\t|\t(3番/30分)")
        score[3]= score[3]+30

    # 3.2　暗刻系列
    matches = [cards for cards in hiddenCards if getKinds(cards)=='槓' or getKinds(cards)=='碰']
    if (len(matches)==2):
        output_Hanname.append("二暗刻\t|\t(X番/5分)")
        score[3] = score[3]+5
    elif (len(matches)==3):
        output_Hanname.append("三暗刻\t|\t(1番/30分)")
        score[3] = score[3]+30
    elif (len(matches)==4):
        output_Hanname.append("四暗刻\t|\t(10番/125分)")
        score[3] = score[3]+125

    #3.3　槓系列
    if len(fourOfAKind)==1:
        output_Hanname.append("一槓\t|\t(X番/5分)")         
        score[3] = score[3]+5    
    elif len(fourOfAKind)==2:
        output_Hanname.append("二槓\t|\t(X番/20分)")         
        score[3] = score[3]+20        
    elif len(fourOfAKind)==3:
        output_Hanname.append("三槓\t|\t(10番/120分)")         
        score[3] = score[3]+120         
    elif len(fourOfAKind)==4:
        output_Hanname.append("四槓\t|\t(40番/480分)")
        score[3] = score[3]+480         
    ###  5同樣花色的順類  ###
    #待修
    #5.1.1 一般高：   有兩副一樣的順子。
    if straight:
        if len(straight)-len(set(straight))==1: #不確定可否這樣寫
            output_Hanname.append("一般高\t|\t(1番/10分)")
            score[4] = score[4]+10
    #5.1.2 兩般高：   兩個一般高（有兩個成對的順子），不需門前清 
        elif len(straight)-len(set(straight))==2 and len(straight)==4:
            output_Hanname.append("兩般高\t|\t(10番/60分)")
            score[4] = score[4]+60

    #5.1.3 太搬高：   3個一樣的順子。
        elif len(straight)==3 and len(straight)-len(set(straight))==2:
            output_Hanname.append("太搬高\t|\t(X番/120分)")
            score[4]= score[4]+120
        elif len(straight)==4 and len(straight)-len(set(straight))==3:
            output_Hanname.append("四海一家\t|\t(40番/480分)")
            score[4]= score[4]+480
    
    ###  6 三個花色  ###
    #胡牌時需有三個顏色的牌組
    
    cardsColor = [getColor(comb) for comb in winCards ]
    if len(set(cardsColor))>=3:
       
            
    
    #6.1 三色同順（三相逢、三姊妹）：3個顏色的順子都是同一個數字 (3個顏色、3個順子、3個順子同個數字)
    #3番/35分
        straightColor = []
        if len(straight)>=3:
            for cards in straight:
                straightColor.append(getColor(cards))
            if len(set(straightColor))==3:
                samecount =0
                samplecards = straight[0]
                for cards in straight:
                    tmpcards = [card%10 for card in cards]
                    if tmpcards == samplecards:
                        samecount=samecount+1
                if samecount ==3:
                    output_Hanname.append("三色同順\t|\t(3番/35分)")
                    score[5] = score[5]+35    
    '''
    #6.2.1 三色小同刻： 2個顏色的刻/槓，加上另一花色的眼都是同一數字
    #？/30分
        if (len(threeOfAKind)+len(fourOfAKind))>=2:
            cardsColor =[]
            tmpcards = []
            tmpcardsNum = []
            tmpcardsKind = []
            for cards in winCards:
                if not getKinds(cards)=='順'：
                    cardsColor.append(getColor(cards))
                    tmpcardsKind.append(getKinds(cards))
                    tmpcards.append(cards)
                    tmpcardsNum.append([card%10 for card in cards])
            if '雀' in tmpcardsKind:
                            
        fourColor = []
        threeNumber = []
        fourNumber = []
        pairColor =[]
        pairNumber =[]
        
    
    6.2.2 三色同刻：3個顏色的刻/槓都是同一個數字
    3番/120分
    '''

    ###  7 連續類  ###
    #同一個花色內數字連續的三組或四組牌

    #7.1 一條龍（一氣通貫）：同一個花色的 123 456 789三個順子。
    for color in s:
        if len(set(color))==9 and sum(set(color))==45:
            output_Hanname.append("一條龍\t|\t(3番/40分)")
            score[6]= score[6]+40        
    '''
    #7.2.1 三連刻（姊妹碰）：同一個花色的 3個連續數字的 3個刻/槓。（EX：[3 3 3] [4 4 4] [5 5 5]）
    for color in s:
        if (len(threeOfAKind)+len(fourOfAKind))==3:
           print ("三連刻") 
           print ("")
    10番/100分
    7.2.2 四連刻（）：同一個花色的 4個連續數字的 4個刻/槓。
    40台/200分    
    '''
    ###  8 么九類  ###
    #8.1.1 混全么： 每一個牌組皆帶有1或9或字牌。
    tmpcards = []    
    for cards in winCards:
        for card in cards:
            if card%10==1 or card%10==9 or getColor(cards)=='字':
                tmpcards.append(cards)
                break
    if z and (len(threeOfAKind)+len(fourOfAKind))==4 and len(tmpcards)==len(winCards):
        output_Hanname.append("混么九\t|\t(10番/100分)" )
        score[7] = score[7]+100

    elif z and len(tmpcards)==len(winCards):
        output_Hanname.append("混全么\t|\t(？番/40分)" )
        score[7] = score[7]+40

    #8.1.4 清么九： 手牌全由么九數牌組成。別稱「清老頭」。     
    elif not z and len(threeOfAKind)==4 and len(tmpcards)==len(winCards):
        output_Hanname.append("清么九\t|\t(？番/400分)" ,"(",listDict(tmpcards,2),")")
        score[7] = score[7]+400
    #8.1.2 純全帶邀： 每一個牌組皆帶有1或9數牌。
    elif not z and len(tmpcards)==len(winCards):
        output_Hanname.append("純全么\t|\t(？番/50分)" , "(",listDict(tmpcards,2),")")
        score[7] = score[7]+50

    ###  9 偶然類  ###
    #因胡牌的時機而加分
    if winTime:
    #9.1.1 海底撈月：摸最後一張海底牌後自摸胡牌的加分。
        if winTime[0]=='海底撈月':
            output_Hanname.append("海底撈月\t|\t(1番/10分)")
            score[8]=score[8]+10
    #9.1.2 海底撈魚：他家摸了海底牌之後打出的牌，放槍而胡。
        elif winTime[0] =='海底撈魚':
            output_Hanname.append("海底撈魚\t|\t(1番/10分)")
            score[8]=score[8]+10
    #9.2 嶺上開花（槓上開花）：槓時補牌->摸牌然後胡牌的加分。
        if winTime[1] =='槓上開花':
            output_Hanname.append("槓上開花\t|\t(1番/10分)")
            score[8]=score[8]+10
    #（△）9.3 搶槓：（？？） 
        if winTime[2] =='搶槓':
            output_Hanname.append("搶槓\t|\t(1番/10分)")
            score[8]=score[8]+10
    #9.4.1 天胡：莊家一取完牌就胡牌的加分。
        if winTime[3] == '天胡':
            output_Hanname.append("天胡\t|\t(20番/155分)")
            score[8]=score[8]+155
        elif winTime[3] == '地胡':
            output_Hanname.append("地胡\t|\t(10番/155分)")
            score[8]=score[8]+155

    
    ###  10 特殊胡牌形  ###
    #基本胡牌型（4組加1對眼）以外的胡牌型，不加計門前清。
    #（△）10.1 國士無雙（十三么九）： 門前清的取得全部的1和9和字牌各一個。
    #40番/160分
    #（△）10.2 七對子： （四隻相同的牌，沒有開槓即可當成兩對）（七對子的分數不能加計所有要求刻槓順的胡牌方式，但可加計除此以外的）
    #7番/30分
    if output_Han:
        for string in output_Hanname:
            print (string)
    verbose = False
    if verbose:
        print ("is it a win pattern?",win)
        print (score)
        
        print ("----------------------------------------")    
    return sum(score) 



    ##################################################################
    ###   傳入2或３或４張牌的list，可得到其牌型，如果不符合任一牌型則回傳None  ###
    ##################################################################


def getKinds(pair): # 得到此list是'槓'、'碰'、還是'吃'、還是'雀'
    #print ("card : ",pair)
    
    if len(pair)==2 and len(set(pair))==1:
        return '雀'
    elif len(pair)==4 and len(set(pair))==1:
        return '槓'
    elif len(pair)==3 :
        pair.sort()
        if len(set(pair))==1:
            return '碰'
        elif len(set(pair))==3:
            return '吃'
    #print (pair, ", it can't form any combination !")
    return None
    #########################################
    ###   傳入2或３或４張牌的list，可得到其花色  ###
    #########################################
def getColor(comb):
    for card in comb:
            if 1 <= card <= 9:
                return '萬'
            elif 11 <= card <=19:
                return '條'
            elif 21 <= card <= 29:
                return '餅'
            else:
                return '字'
def listDict(ls,num):
    ls_map =[]
    if num==1:
        for card in ls:
            ls_map.append(CardIndex[card])
       
    elif num==2:
        for cards in ls:
            lstmp = []
            for card in cards:
                lstmp.append(CardIndex[card])
            ls_map.append(lstmp)
      
    return ls_map      
'''
winCards=[[13, 14, 15], [25, 25], [26, 26, 26 , 26], [14, 15, 16], [22, 23, 24]]
hiddenCards=[[13, 14, 15], [25, 25]]
openCards = [[26, 26, 26, 26], [14, 15, 16], [22, 23, 24]]
'''

if __name__ == '__main__':
    winCards=[[10, 10, 10], [20, 20, 20], [0, 0, 0], [30, 30, 30], [31, 31]]
    hiddenCards=[[10, 10, 10], [20, 20, 20], [0, 0, 0], [30, 30, 30], [31, 31]]
    openCards= []
    score = getScore( 2 , winCards, hiddenCards , openCards )

    print ("Scores = ",score)
