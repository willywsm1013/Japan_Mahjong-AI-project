#-*- coding: utf-8 -*-　
import random
from Agent import Agent

########################
###   Random Agent   ###
########################
class RandomAgent(Agent):
    
    def takeAction(self,newCard):
        if newCard != None :
            self.handcard.append(newCard)
        
        result,cardCombination = self.goalTest()
        
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
        maxUtil = max([info[3] for info in infos])
        throwCard = random.choice([info[0] for info in infos if info[3] == maxUtil])
        self.handcard.remove(throwCard)
        return throwCard
        print (throwCards)
        
        print (len(infos))
        for info in infos :
            print (info)
        assert 0==1
