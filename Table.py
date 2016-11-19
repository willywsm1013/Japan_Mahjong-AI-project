import BasicDefinition
import numpy as np 
from Agent import Agent
import random
class Table:
    MAX_Agent = 4
    currentAgent = 0
    deck = []
    def newGame(self) :
        self.agents = []
        self.deckInitial()

    def addAgent(self,action):
        if len(self.agents) < self.MAX_Agent :
            self.agents.append(Agent(len(self.agents),action))
        else :
            print ('Agent reach the maximum agent number!')
    
    def deal(self) :
        self.shuffleDeck()
        if len(self.agents) != self.MAX_Agent:
            print ('Current agent number : ', len(self.agents))
            print ('No enough agents')
        else :
            for agent in self.agents:
                handCard = self.deck[0:13]
                self.deck = self.deck[13::]
                agent.initialHandCard(handCard)
    
    def pickCard(self):
        return self.deck.pop()

    def deckInitial(self):
        self.deck = []
        for i in xrange(34):
            if i < 34 :
                self.deck.append([i]*4)    
            else :
                self.deck.append([i])
        self.deck = sum(self.deck,[])

    def shuffleDeck(self):
        random.shuffle(self.deck)    
        
'''
    testing part
'''
def f():
    pass
if __name__ == '__main__' :
    table = Table()
    table.newGame()
    for i in xrange(4):
        table.addAgent(f)
    table.deal()
    print (table.deck)
    print (len(table.deck))
