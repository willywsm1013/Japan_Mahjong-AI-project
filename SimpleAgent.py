#-*- coding: utf-8 -*-　
import random
from BasicDefinition import *
from Agent import Agent
from util import *
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
    def takeAction(self,newCard,verbose):
        if newCard!= None:
            self.handcard.append(newCard)
        result, cardCombination = self.goalTest()

        assert result or cardCombination == None
        if result:
            return '自摸',cardCombination+self.cardsOnBoard[self.playerNumber]
        else:
            return 'Throw' , self.OneStepwithScore() 


    def OneStepwithScore(self):
        evaluate = True
        infos = self.xiangtingshu(self.handcard,evaluate)
        if len(infos[0])==5:
            ValueList = [info[4] for info in infos]
            maxValue = max(ValueList)
            throwCard = random.choice([info[0] for info in infos if info[4] == maxValue])
            print ("score choose",maxValue)
        else:
            maxUtil = max([info[3] for info in infos]) #info[3]為有效牌總數，選擇最大的那個
            throwCard = random.choice([info[0] for info in infos if info[3] == maxUtil])
        
        return throwCard
        print (throwCards)
        
        print (len(infos))
        for info in infos :
            print (info)

