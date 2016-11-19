#-*- coding: utf-8 -*-　
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

    def gameStart(self):
        self.currentAgent = random.randint(0,3)
        newCard = self.pickCard()
        while True:
            state ,throwCard = self.agents[self.currentAgent].takeAction(newCard)
            if state == 'Win' :
                break
            ## find who is the next
            nextAgent = (self.currentAgent+1) % self.MAX_Agent
            for i in xrange(self.MAX_Agent):
                if i != self.currentAgent:
                    tmpState,tmpCards= self.agents[self.currentAgent].check(self.currentAgent,throwCard)
                    ## priority of 吃 is higher than 槓 
                    if tmpState == '吃' or (tmpState == '槓' and state != '吃'):
                        state = tmpState
                        cards = tmpCards
                        nextAgent = i
            
            self.currentAgent = nextAgent
            if state == '吃' or state == '槓':
                assert throwCard != None
                newCard = throwCard
                ## broadcast information
                for i in xrange(self.MAX_Agent):
                    if i != nextAgent :
                        self.agents[i].update(nextAgent,cards)
            else :
                newCard = self.pickCard()
                ## if deck is empty it means on winner in this round
                if newCard == None :
                    state = 'No winner'
                    break

        if state == 'Win' :
            print ('The winner is : ',self.currentAgent)
        elif state == 'No winner' :
            print (state)
        

    def pickCard(self):
        if len(self.deck) != 0:
            return self.deck.pop()
        else:
            return None
            
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
    table.gameStart()
