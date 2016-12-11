#-*- coding: utf-8 -*-　
import random
from Agent import Agent

########################
###   Random Agent   ###
########################
class RandomAgent(Agent):
    def __init__(self,player_number):
        self.handcard = None
        self.cardsOnBoard = [[],[],[],[]]
        self.cardsThrowed = [[],[],[],[]]
        self.playerNumber = player_number
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
            

