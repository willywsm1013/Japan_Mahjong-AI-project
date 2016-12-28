#-*- coding: utf-8 -*-　
import random
from Agent import Agent

########################
###   Random Agent   ###
########################
class RandomAgent(Agent):# 繼承自class Agent的class
    
    def takeAction(self,newCard):
        if newCard != None :
            self.handcard.append(newCard)
        
        result,cardCombination = self.goalTest()# result 是 True /False，cardCombination 是手牌
        
        assert result or cardCombination == None
        if result:
            return '自摸',cardCombination+self.cardsOnBoard[self.playerNumber]
        else:
            return 'Throw',self.randomAction()

    def randomAction(self):
        return self.handcard.pop(random.randrange(len(self.handcard)))


#def RandomAction(handCards):
            
##########################
###   One step Agent   ###
###   利用向聽數的Agent   ###
##########################
class OneStepAgent(Agent):
    
    def takeAction(self,newCard):
        if newCard != None :
            self.handcard.append(newCard)
        
        result,cardCombination = self.goalTest()
        
        assert result or cardCombination == None
        if result:
            return '自摸',cardCombination+self.cardsOnBoard[self.playerNumber]
        else:
            return 'Throw',self.OneStep()

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
        assert 0==1

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

