#-*- coding: utf-8 -*-　
import BasicDefinition
import numpy as np 
from six.moves import cPickle
from Agent import Agent
from BasicDefinition import CardIndex
import random
from SimpleAgent import RandomAgent,OneStepAgent

class Table:
    MAX_Agent = 4
    currentAgent = 0
    deck = []
    def newGame(self) :
        self.agents = []
        self.deckInitial()

    def addAgent(self,newAgent):
        if len(self.agents) < self.MAX_Agent :
            self.agents.append(newAgent)
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
            
                       
            if state == '自摸' : 
                if verbose :
                    print ('Agent ',i,':',state,end=' [ ')
                    for cards in throwCard:
                        print ('[ ',end='')
                        for card in cards:
                            print (CardIndex[card],end=',')
                        print ('\b],',end='')
                    print ('\b]')
                break
            
            ###
            if verbose : print ('Throw ',CardIndex[throwCard])
            ###

            assert throwCard < 34 and throwCard >= 0,('the card you throw is ',throwCard)
            ## find who is the next
            nextAgent = (self.currentAgent+1) % self.MAX_Agent
            for i in range(self.MAX_Agent):
                if i != self.currentAgent:
                    agent = self.agents[i]
                    info = agent.check(self.currentAgent,throwCard)
                    tmpCards = info[0]#[1 1 1]
                    tmpState = info[1]#'吃'、'碰'、'槓'
                    assert throwCard == info[2]#丟出來的那張
                    
                    ###
                    if verbose : 
                        print ('Agent ',i,':',tmpState,end=' [ ')
                        if tmpState == '胡':
                            print (tmpCards)
                            for cards in tmpCards:
                                print ('[ ',end='')
                                for card in cards:
                                    print (CardIndex[card],end=',')
                                print ('\b],',end='')
                        else:
                            for card in tmpCards :
                                print (CardIndex[card],end=',')
                        print ('\b]')
                        #input()
                    ###
                    assert self.__cardChecker(tmpCards,tmpState) 
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
                loseAgent = self.currentAgent
                break
			            
            if state == '吃' or state == '碰' or state == '槓':
                if verbose :
                    print ('Agent ',nextAgent,' get ',CardIndex[throwCard])
                takeAgent = nextAgent            
                takeCards = cards                
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
                takeAgent = None
                takeCards = None
                newCard = self.pickCard()
                ## if deck is empty it means no winner in this round
                if newCard == None :
                    state = '流局'
                    break

            ## broadcast information
            for i in range(self.MAX_Agent):
                self.agents[i].update(self.currentAgent,takeAgent,takeCards,throwCard)
            self.currentAgent = nextAgent
            print ('-------------------------------------')

        if state == '胡' :
            print ('贏家 : ',winAgent)
            print ('放槍 : ',loseAgent)
            return winAgent
        elif state == '自摸':
            print (self.currentAgent,'自摸')
            return self.currentAgent
        elif state == '流局' :
            print (state)
            return None
        else:
            assert 0==1
        

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

    def __cardChecker(self,cards,state):
        if state != '胡':
            assert all([(card < 34 and card >= 0) for card in cards])
        error = True
        if len(cards)==0 and state == '過':
            error=False
        elif len(cards) == 4 and len(set(cards)) == 1 and state == '槓':
            error = False
        elif len(cards) == 3 and len(set(cards)) == 1 and state == '碰':
            error = False
        elif len(cards) == 3 and len(set(cards)) == 3:
            if all([(card > 0 and card < 10) or (card>10 and card < 20) or (card>20 and card<30) for card in cards]):
                cards = sorted(cards)
                if cards[0]+1 == cards[1] and cards[1]+1 == cards[2] :
                    error=False
        elif state=='胡' and len(cards)>=5:
            error = False
            for card in cards:
                if len(card)==2 and card[0]==card[1]:
                    pass
                elif len(card)==3:
                    cardLen = len(set(card))
                    if cardLen==3 and card[0]+1==card[1] and card[1]+1==card[2]:
                        pass
                    elif cardLen == 1:
                        pass
                    else:
                        error=True
                        break
                elif len(card)==4 and len(set(card))==1:
                    pass
                else :
                    error=True
                    break
        else :
            print (cards)
            print (state)
            assert 0==1
        if error :
            print ('state : ',state,', cards : ',cards)
            print ('card Checkerror')

        return not error
'''
    testing part
'''

def f():
    pass
if __name__ == '__main__' :
    table = Table()
    record = [0]*4
    repeat = 100.0
    for time in range(int(repeat)):
        table.newGame()
        for i in range(3):
            table.addAgent(RandomAgent(i))
        table.addAgent(OneStepAgent(3))
        table.deal()
        winner = table.gameStart(True)
        if winner != None:
            record[winner]+=1
    print (record)
