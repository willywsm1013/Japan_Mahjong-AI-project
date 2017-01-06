#-*- coding: utf-8 -*-　
import random
from BasicDefinition import *
from Agent import Agent
from util import *
import math
from getScore import getScore
########################
###   Random Agent   ###
########################
class RandomAgent(Agent):# 繼承自class Agent的class
    
    def takeAction(self,newCard,verbose):
        if newCard != None :
            self.handcard.append(newCard)
        
        result,cardCombination = self.goalTest()# result 是 True /False，cardCombination 是手牌
        
        assert result or cardCombination == None
        if result:
            return '自摸',[cardCombination,self.cardsOnBoard[self.playerNumber]]
        else:
            return 'Throw',self.randomAction()

    def randomAction(self):
        return self.handcard.pop(random.randrange(len(self.handcard)))


#def RandomAction(handCards):
            
#############################
###   One step Agent      ###
###   利用向聽數的Agent   ###
#############################
class OneStepAgent(Agent):
    
    def takeAction(self,newCard,verbose):
        if newCard != None :
            self.handcard.append(newCard)
        
        result,cardCombination = self.goalTest()
        
        assert result or cardCombination == None
        if result:
            return '自摸',[cardCombination,self.cardsOnBoard[self.playerNumber]]
        else:
            return 'Throw',self.OneStep()

    def OneStep(self):
        infos = self.xiangtingshu(self.handcard)
        maxUtil = max([info[3] for info in infos]) #info[3]為有效牌總數，選擇最大的那個
        throwCard = random.choice([info[0] for info in infos if info[3] == maxUtil])
        self.handcard.remove(throwCard)
        return throwCard

##########################
###   Simple Defense   ###
##########################
class SimpleDefenseAgent(Agent):
    def takeAction(self,newCard,verbose):
        if newCard != None :
            self.handcard.append(newCard)
        
        result,cardCombination = self.goalTest()
        
        assert result or cardCombination == None
        if result:
            return '自摸',[cardCombination,self.cardsOnBoard[self.playerNumber]]
        else:
            return 'Throw',self.SimpleDefense(verbose)
 
    def check(self,agentNum,card):
        self.handcard.append(card)
        result,cardCombination = self.goalTest()
        if result:
            return [[cardCombination,self.cardsOnBoard[self.playerNumber]], '胡', card]
        self.handcard.remove(card)

        return [[],'過',card] 
    
    def SimpleDefense(self,verbose):
        maxNumber = 8
        if len(self.cardsThrowedNoTaken) <= maxNumber :
            cards = self.cardsThrowedNoTaken[:]
        else:
            cards = self.cardsThrowedNoTaken[-maxNumber:]
        
        safeCards = [card for card in cards if card in self.handcard] 
        prob = [self.computeProb(card) for card in self.handcard]
        if verbose:
            print ('Handcard : ',self.handcard)
            for i in range(len(self.handcard)):
                card = self.handcard[i]
                p = prob[i]
                print ('    ',CardIndex[card],' : ',p)
        #input()
        return self.decision(safeCards,prob,verbose)
    
    def computeProb(self,card):
        prob = []
        unknownNum = 34*4-len(self.cardOpened)-len(self.handcard)
        otherPlayer = [i for i in range(4) if i != self.playerNumber] 
        handCardNum = [13 - len(self.cardsOnBoard[i])*3 for i in otherPlayer if i != self.playerNumber] ## agent i 手上剩幾張牌
        assert len(handCardNum) == 3
        ## 檢查組成 雀 刻 槓 的機率
        left = 4 - self.cardOpened.count(card) - self.handcard.count(card)
        assert left >= 0,('card:',card,' cardsOpened:',self.cardOpened)
        if left > 0: ## 剩下多於一張牌不知道在哪裡時才有機會組成 雀頭 刻 槓
            notInHand = unknownNum - sum(handCardNum)
            ## p(組成雀刻槓) = 1 - p(全部都在牌山中)
            prob.append(1 - C(unknownNum-left,notInHand-left)/C(unknownNum,notInHand))
            #print ((left,handCardNum,unknownNum))
        
        ## 檢查被吃的機率
        pairs = []
        if int(card/10) < 3 and card%10 !=0 :
            number = card%10
            if number <= 7: ## 檢查本身和右邊兩張
                leftR1 = 4 - self.cardOpened.count(card+1) - self.handcard.count(card+1) ## 右邊一張
                leftR2 = 4 - self.cardOpened.count(card+2) - self.handcard.count(card+2) ## 右邊兩張
                if leftR1 != 0 and leftR2 != 0:
                    pairs.append((leftR1,leftR2))
            if number >=3: ## 檢查本身和左邊兩張
                leftL1 = 4 - self.cardOpened.count(card-1) - self.handcard.count(card-1) ## 左邊一張
                leftL2 = 4 - self.cardOpened.count(card-2) - self.handcard.count(card-2) ## 左邊兩張
                if leftL1 != 0 and leftL2 != 0:
                    pairs.append((leftL1,leftL2))

            if number >= 2 and number <= 8: ## 檢查自己和左右各一張
                leftR = 4 - self.cardOpened.count(card+1) - self.handcard.count(card+1) ## 右邊一張
                leftL = 4 - self.cardOpened.count(card-1) - self.handcard.count(card-1) ## 左邊一張
                if leftR != 0 and leftL != 0:
                    pairs.append((leftR,leftL))
            
            for pair in pairs : 
                l1 = pair[0]
                l2 = pair[1]
                pt = 1
                for n in handCardNum :
                    p = l1*l2*n*(n-1)/unknownNum/(unknownNum-1)
                    pt *= (1-p)
                pt = 1-pt
                prob.append(pt)

        prob  = [1-p for p in prob]
        pt = 1
        for p in prob:
            pt *= p
        pt = 1-pt
                        
        return pt
    
    def decision(self,safeCards,prob,verbose):
        choice = [card for card in safeCards if prob[self.handcard.index(card)] > 0.2]
        if len(choice) !=0 :
            p = [prob[self.handcard.index(card)] for card in choice ]
            throw = choice[p.index(max(p))]
            if verbose :
                print ('select from safe card')
        else :
            minProb = min(prob)
            chosen = [self.handcard[i] for i in range(len(self.handcard)) if prob[i] == minProb]
            throw = random.choice(chosen)
            if verbose :
                print ('select by probability')
        if verbose :
            print ('throw ',CardIndex[throw])
        
        self.handcard.remove(throw)
        return throw

class ValueAgent(Agent):
    def takeAction(self,newCard):
        if newCard!= None:
            self.handcard.append(newCard)
        result, cardCombination = self.goalTest()

        assert result or cardCombination == None
        if result:
            return '自摸',cardCombination+self.cardsOnBoard[self.playerNumber]
        else:
            infos = self.xiangtingshu(self.handcard)
            xiangtingNum = infos[0][1]
            maxValue = max([info[4] for info in infos])
            if xiangtingNum>3:
                return 'Throw' ,self.OneStep()
            else:
                return 'Throw' , self.SearchValue() 

    def SearchValue():
        pass
    
    def OneStep(self):
        infos = self.xiangtingshu(self.handcard)
        maxUtil = max([info[3] for info in infos]) #info[3]為有效牌總數，選擇最大的那個
        throwCard = random.choice([info[0] for info in infos if info[3] == maxUtil])
        self.handcard.remove(throwCard)
        return throwCard
        print (throwCards)
        
        print (len(infos))
        for info in infos :
            print (info)

    def OneStepwithScore(self):
        infos = self.xiangtingshu(self.handcard)
        maxUtil = max([info[4] for info in infos])
        throwCard = random.choice([info[0] for info in infos if info[4] == maxUtil])
        self.handcard.remove(throwCard)
        return throwCard
        print (throwCards)
        
        print (len(infos))
        for info in infos :
            print (info)

class MCTSAgent(Agent):
    def takeAction(self,newCard,verbose):
        if newCard!= None:
            self.handcard.append(newCard)
        result, cardCombination = self.goalTest()

        assert result or cardCombination == None
        if result:
            return '自摸',cardCombination+self.cardsOnBoard[self.playerNumber]
        else:
            infos = self.xiangtingshu(self.handcard)
            xiangtingNum = infos[0][1]
            maxValue = max([info[4] for info in infos])
            if xiangtingNum>3:
                return 'Throw' ,self.OneStep()
            else:
                return 'Throw' , self.SearchScore() 

    def SearchScore(self):
        cardType = []
        for card in self.handcard:
            if card not in cardType:
                cardType.append(card)
        cardTypeNum = len(cardType)
        
        ucb = [0.0]*cardTypeNum
        selectedTime = [1.0]*cardTypeNum
        totalTime = cardTypeNum
        scoreSum = [0.0]*cardTypeNum
        repeat = 1000
        for time in range(repeat):
            maxUcb = max(ucb)
            cardIndex = random.choice([i for i in range(cardTypeNum) if ucb[i] == maxUcb])
            selectedTime[cardIndex] += 1
            totalTime += 1
            chosedCard = cardType[cardIndex]

            #模擬遊戲
            remainCard = self.findRemainCard()
            random.shuffle(remainCard)
            agents = []
            scoreBoard = [0]*4
            for i in range(4):
                agents.append(RandomAgent(i))
                if i == self.playerNumber:
                    agents[i].handcard = self.handcard    #chosedCard還沒丟出去
                else:
                    cardNum = 13 - len(self.cardsOnBoard[i])*3
                    agents[i].handcard = remainCard[0:cardNum]
                    remainCard = remainCard[cardNum::]


            #####################################################
            currentAgent = self.playerNumber
            for i in range(4):
                wind = WindIndex[i]
                agent = agents[(i+currentAgent)%4]
                agent.setWind(wind)
            firstRound = True
            newCard = None
            while True:
                agent  = agents[currentAgent]
                state = None
                throwCard = None
                if firstRound:    #第一輪是該玩家丟出選擇的牌
                    state = 'Throw'
                    throwCard = chosedCard
                    agent.handcard.remove(throwCard)
                    firstRound = False
                else:
                    state ,throwCard = agent.takeAction(newCard,verbose)               
                            
                if state == '自摸' : 
                    cards = throwCard
                    winAgent = currentAgent
                    break

                assert throwCard < 34 and throwCard >= 0,('the card you throw is ',throwCard)
                ## find who is the next
                nextAgent = (currentAgent+1) % 4
                for i in range(4):
                    if i != currentAgent:
                        agent = agents[i]
                        info = agent.check(currentAgent,throwCard)
                        tmpCards = info[0]#[1 1 1]
                        tmpState = info[1]#'吃'、'碰'、'槓'
                        assert throwCard == info[2]#丟出來的那張
                    
                        if tmpState == '過':
                            continue
                    
                        ## 胡 > 碰槓 > 吃
                        if tmpState == '胡' :
                            nextAgent = i
                            cards = tmpCards
                            state = tmpState
                            break
                        if tmpState == '碰':
                            assert state != '槓' and state != '碰'
                            state = tmpState
                            cards = tmpCards
                            nextAgent = i
                        elif tmpState == '槓':
                            assert state != '碰' and state != '槓'
                            state = tmpState
                            cards = tmpCards
                            nextAgent = i
                        elif tmpState == '吃' and (state != '碰' or state != '槓'):
                            state = tmpState
                            cards = tmpCards
                            nextAgent = i
                        else :
                            print ('No define state \'',tmpState,"\'")
                            sys.exit()
            
            
                if state == '胡':
                    winAgent = nextAgent
                    loseAgent = currentAgent
                    break
			            
                if state == '吃' or state == '碰' or state == '槓':
                    takeAgent = nextAgent            
                    takeCards = cards                

                    if state == '槓':
                        newCard = self.pickCard(remainCard)
                        ## if deck is empty it means no winner in this round
                        if newCard == None :
                            state = '流局'
                            break
                    else:
                        #newCard = throwCard
                        newCard = None

                else:
                    takeAgent = None
                    takeCards = None
                    newCard = self.pickCard(remainCard)
                    ## if deck is empty it means no winner in this round
                    if newCard == None :
                        state = '流局'
                        break

                ## broadcast information
                for i in range(4):
                    agents[i].update(currentAgent,takeAgent,takeCards,throwCard,verbose)
                currentAgent = nextAgent

            if state == '胡' :
                #print ('贏家 : ',winAgent)
                #print ('放槍 : ',loseAgent)
                score = getScore(winAgent,cards[0]+cards[1],cards[0],cards[1],self.agents[winAgent].wind)
                scoreBoard[winAgent] += score * 3
                if score <= 25:
                    for i in range(4):
                        if i != winAgent :
                            scoreBoard[i] -=score
                else :
                    scoreBoard[loseAgent] -= (score*3 -50)
                    for i in range(4):
                        if i != winAgent and i != loseAgent:
                            scoreBoard[i] -= 25

                #return winAgent,loseAgent,self.scoreBoard
            elif state == '自摸':
                print (winAgent,'自摸')
                score = getScore(winAgent,cards[0]+cards[1],cards[0],cards[1],agents[winAgent].wind)
                scoreBoard[winAgent] += score * 3
                for i in range(4):
                    if i != winAgent :
                        scoreBoard[i] -=score

                #return winAgent,None,scoreBoard
            #elif state == '流局' :
                #print (state)
                #return None,None,None
            #else:
                #assert 0==1

        #########################################################

            scoreSum[cardIndex] += scoreBoard[self.playerNumber]
            for i in range(cardTypeNum):
                ucb[i] = scoreSum[i]/selectedTime[i] + math.sqrt(2*math.log(totalTime)/selectedTime[i])

        avgScore = []
        for i in range(cardTypeNum):
            avgScore[i] = scoreSum[i]/selectedTime[i]
        throwCard = cardType[avgScore.index(max(avgScore))]
        return throwCard
        
    def findRemainCard(self):
        deck = []
        for i in range(34):
            deck.append([i]*4)
        deck = sum(deck, [])
        for card in self.cardOpened:
            deck.remove(card)
        for card in self.handcard:
            deck.remove(card)
        return deck

    def pickCard(self, cards):
        if len(cards) > 0:
            return cards.pop()
        else:
            return None
        
    
    def OneStep(self):
        infos = self.xiangtingshu(self.handcard)
        maxUtil = max([info[3] for info in infos]) #info[3]為有效牌總數，選擇最大的那個
        throwCard = random.choice([info[0] for info in infos if info[3] == maxUtil])
        self.handcard.remove(throwCard)
        return throwCard

