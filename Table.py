#-*- coding: utf-8 -*-　
import BasicDefinition
import numpy as np 
from Agent import Agent
from BasicDefinition import CardIndex
import random
from SimpleAction import RandomAction
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

    def gameStart(self,verbose = False):
        print ('Game start !')
        self.currentAgent = random.randint(0,3)
        print ('Agent ',self.currentAgent,' is first!')
        print ('-------------------------------------')
        newCard = self.pickCard()
        while True:
            ###
            if verbose :
                
                print ('current handcards for every agent :')
                for agent in self.agents :
                    agent.printHandCard()
                print ("\nAgent ",self.currentAgent,"'s action")
            ###
            
            agent  = self.agents[self.currentAgent]
            if newCard != None :
                print ('get ',CardIndex[newCard]) 
            state ,throwCard = agent.takeAction(newCard)
            
            ###
            if verbose : print ('Throw ',CardIndex[throwCard])
            ###
            
            if state == '胡' :
                break
            assert throwCard < 34 and throwCard >= 0,('the card you throw is ',throwCard)
            ## find who is the next
            nextAgent = (self.currentAgent+1) % self.MAX_Agent
            for i in range(self.MAX_Agent):
                if i != self.currentAgent:
                    agent = self.agents[i]
                    info = agent.check(self.currentAgent,throwCard)
                    tmpCards = info[0]
                    tmpState = info[1]
                    assert throwCard == info[2]
                    
                    ###
                    if verbose : 
                        print ('Agent ',i,':',tmpState,end=' [ ')
                        for card in tmpCards :
                            print (CardIndex[card],end=',')
                        print ('\b]')
                        input()
                    ###
                    
                    if tmpState == '過':
                        continue
                    
                    ## 胡 > 碰槓 > 吃
                    if tmpState == '胡' :
                        nextAgent = i
                        cards = tmpCards
                        state = tmpState
                        break
                    if tmpState == '碰':
                        assert len(tmpCards) == 3,('cards : ',tmpCards,', 碰 should have 3 cards')
                        assert state != '槓' and state != '碰'
                        assert self.__cardCheck(tmpCards) == tmpState,('cards :',tmpCards,
                                                                       ' agent say state is ',tmpState.decode(' utf-8'))
                        state = tmpState
                        cards = tmpCards
                        nextAgent = i
                    elif tmpState == '槓':
                        assert len(tmpCards) == 4, ('cards : ',tmpCards,', 槓 should have 4 cards')
                        assert state != '碰' and state != '槓'
                        assert self.__cardCheck(tmpCards) == tmpState,('cards :',tmpCards,
                                                                       ' agent say state is ',tmpState.decode(' utf-8'))
                        state = tmpState
                        cards = tmpCards
                        nextAgent = i
                    elif tmpState == '吃' and (state != '碰' or state != '槓'):
                        assert len(tmpCards) == 3,('cards : ',tmpCards,', 吃 should have 3 cards')
                        assert self.__cardCheck(tmpCards) == tmpState,('cards :',tmpCards,
                                                                       ' agent say state is ',tmpState.decode('utf-8'))
                        state = tmpState
                        cards = tmpCards
                        nextAgent = i
                    else :
                        print ('No define state \'',tmpState,"\'")
                        sys.exit()
                                     
            if state == '胡':
                break
            elif state == '吃' or state == '碰' or state == '槓':
                if verbose :
                    print ('Agent ',nextAgent,' get ',CardIndex[throwCard])
                ## broadcast information
                for i in range(self.MAX_Agent):
                    self.agents[i].update(nextAgent,[cards,state,throwCard])

                if state == '槓':
                    newCard = self.pickCard()
                    ## if deck is empty it means no winner in this round
                    if newCard == None :
                        state = '流局'
                        break
                else:
                    #newCard = throwCard
                    newCard = None

            else :
                if verbose:
                    print ('No agnet get ',CardIndex[throwCard])
                for i in range(self.MAX_Agent):
                    self.agents[i].update(self.currentAgent,[[],'過',throwCard])

                newCard = self.pickCard()
                ## if deck is empty it means no winner in this round
                if newCard == None :
                    state = '流局'
                    break
            
            self.currentAgent = nextAgent
            print ('-------------------------------------')

        if state == '胡' :
            print ('The winner is : ',self.currentAgent)
        elif state == '流局' :
            print (state)
        

    def pickCard(self):
        if len(self.deck) != 0:
            return self.deck.pop()
        else:
            return None
            
    def deckInitial(self):
        self.deck = []
        for i in range(34):
            if i < 34 :
                self.deck.append([i]*4)    
            else :
                self.deck.append([i])
        self.deck = sum(self.deck,[])

    def shuffleDeck(self):
        random.shuffle(self.deck)    

    def __cardCheck(self,cards):
        assert all([(card < 34 and card >= 0) for card in cards])
        if len(cards) == 4 and len(set(cards)) == 1:
            return '槓'
        if len(cards) == 3 and len(set(cards)) == 1:
            return '碰'
        if len(cards) == 3 and len(set(cards)) == 3:
            if all([(card > 0 and card < 10) or (card>10 and card < 20) or (card>20 and card<30) for card in cards]):
                cards = sorted(cards)
                if cards[0]+1 == cards[1] and cards[1]+1 == cards[2] :
                    return '吃'

        return None
'''
    testing part
'''

def f():
    pass
if __name__ == '__main__' :
    table = Table()
    table.newGame()
    for i in range(4):
        table.addAgent(RandomAction)
    table.deal()
    table.gameStart(True)
