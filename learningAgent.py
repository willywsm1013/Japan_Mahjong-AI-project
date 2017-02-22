#-*- coding: utf-8 -*-　
from Agent import *
import util 
import random
import os
import math
from six.moves import cPickle
from collections import namedtuple
class QLearningAgent(Agent):
    
    def __init__(self,player_number,params,mode):
        Agent.__init__(self,player_number)
        self.epsilon = params.epsilon
        self.discount = params.discount
        self.lr = params.learning_rate
        #self.lr_decay = params.lr_decay_fn
        self.lr_decay = None
        self.mode = mode
        print ('epsilon :',self.epsilon)   
        print ('learning :',self.lr)
        print ('discount :',self.discount)

        self.setLearningTarget()
        self.reset()
        
        if params.load_dir != None:
            self.load(params.load_dir)
            
    def reset(self):
        Agent.reset(self)
        self.lastState = None
        self.lastAction = None
        self.recordQ = []
    
    def takeAction(self,newCard,verbose):
        if newCard != None :
            self.handcard.append(newCard)
        
        result,cardCombination = self.goalTest()# result 是 True /False，cardCombination 是手牌
        
        assert result or cardCombination == None
        
        if result:
            return '自摸',[cardCombination,self.cardsOnBoard[self.playerNumber]]
        else:
            self.updateQ(terminate = False)
            return 'Throw',self.takeActionByQ()
    
    def check(self,agentNum,card):
        ### 先檢查有沒有胡牌
        self.handcard.append(card)
        result,cardCombination = self.goalTest()
        if result:
            return [[cardCombination,self.cardsOnBoard[self.playerNumber]], '胡', card]
        self.handcard.remove(card)
        
        self.updateQ(terminate = False,card = card, agent=agentNum)
        ### 取得legal actions
        Property = namedtuple('Property',['terminate','mode','card','agent'])
        prop = Property(False,'take',card,agentNum)

        currentState = self.getState(prop)
        legalActions = self.getLegalActions(currentState)
        
        if self.mode=='train' and util.flipCoin(self.epsilon) :
            action = random.choice(legalActions)
        else :
            qValues= self.getQValue(state=currentState,actions = legalActions)
            maxQ = max(qValues)
            self.recordQ.append(maxQ)
            maxActions = [ legalActions[i] for i in range(len(legalActions)) if qValues[i] == maxQ]
            action = random.choice(maxActions)
        
        self.lastState = currentState
        self.lastAction = action
        #print ('handcard:',self.handcard)
        #print ('card:',card)
        #print ('action:',action)
        #input()
        if action == None :
            return [[], '過', card]
        elif len(action[0]) == 4 and len(set(action[0])) == 1:
            return [list(action[0]),'槓',card]
        elif len(action[0]) == 3 and len(set(action[0])) == 1:
            return [list(action[0]),'碰',card]
        elif len(action[0]) == 3 and len(set(action[0])) == 3 :
            return [list(action[0]),'吃',card]
        else :
            print ('Unlegal action in check :',action)
            raise Exception
    
    #######################################
    ###   用Q value決定要採取的action   ###
    #######################################
    def takeActionByQ(self):

        Property = namedtuple('Property',['terminate','mode'])
        prop = Property(False,'throw')

        currentState = self.getState(prop)
        legalActions = self.getLegalActions(currentState) 
        
        if self.mode=='train' and util.flipCoin(self.epsilon) :
            throw = random.choice(legalActions)
        else :
            qValues= self.getQValue(state=currentState,actions = legalActions)
            maxQ = max(qValues)
            self.recordQ.append(maxQ)
            maxActions = [ legalActions[i] for i in range(len(legalActions)) if qValues[i] == maxQ]
            throw = random.choice(maxActions)
         
        self.handcard.remove(throw)
        
        self.lastState = currentState
        self.lastAction = throw
        
        return throw
    
    def getState(self,prop):
        State = namedtuple('State',['content','property'])
        state = State(self.getContent(),prop)
        return state

    ###############################
    ###   有兩種模式：          ###
    ###   (1)丟牌的時候         ###
    ###   (2)決定吃碰槓的時候   ###
    ###############################
    def getLegalActions(self,state):
        prop = state.property
        content = state.content
       
        mode = prop.mode
        terminate = prop.terminate
        handcards = content.handcards

        if terminate:
            return (None,)
        ### legal action : 手上不重複的牌
        if mode == 'throw':
            return tuple(set(handcards))
        ### legal action : ((可能湊成的組合),不在手上的那張牌)
        elif mode == 'take':
            card = prop.card
            agent = prop.agent
            
            assert card !=None
            legalActions = [None]
            ## 檢查刻
            if handcards.count(card) == 2:
                legalActions.append(((card,card,card),card))
            ## 檢查槓
            if handcards.count(card) == 3:
                legalActions.append(((card,card,card,card),card))

            ## 檢查順
            sub = self.playerNumber - agent
            if (sub == 1 or sub == -3) and int(card/10) < 3 and card%10 != 0 :
                if card % 10 < 8 and ((card+1) in handcards) and ((card+2) in handcards):
                    legalActions.append(((card,card+1,card+2),card))
                if card % 10 !=1 and card%10 != 9 and ((card-1) in handcards) and ((card+1) in handcards):
                    legalActions.append(((card-1,card,card+1),card))
                if card % 10 > 2 and ((card-1) in handcards) and ((card-2) in handcards):
                    legalActions.append(((card-2,card-1,card),card))
            return tuple(legalActions)
                
        else:
            print ('No mode :', mode,' for getLegalActions')
            raise Exception
    
    def decreaseEpsilon(self,proportion):
        self.epsilon *= proportion
    def setEpsilon(self,epsilon):
        if epsilon < 0:
            self.epsilon = 0
        else:
            self.epsilon = epsilon
    
    def lrDecay(self):
        print ('learning rate :',self.lr,' -> ',end='')
        if self.lr_decay != None:
            self.lr = self.lr_decay(self.lr)
        print (self.lr)
    
    #----------------------------------#
    #     modified functions below     #
    #----------------------------------#
    def gameEnd(self,win,lose,score):
        raise NotImplementedError
        Agent.gameEnd(self,score)
        self.updateQ(terminate = True, reward = score)

    def setLearningTarget(self): 
        raise NotImplementedError
            
    def updateQ(self,terminate,reward = 0):
        raise NotImplementedError
        
    def getReward(self):
        raise NotImplementedError
    
    def getQValue(self,state,actions):
        raise NotImplementedError
        
    def getContent(self):
        raise NotImplementedError
    
    def save(self,pickle_name):
        raise NotImplementedError

    def load(self,pickle_name):
        raise NotImplementedError
   
class WeightLearningAgent(QLearningAgent):
    def __str__(self):
        information = """
Agent : WeightLearningAgent
Weight :
"""
        for key in self.weights:
            seq = '    '+key+" : "+str(self.weights[key])+"\n"
            information+=seq

        return information

    def setLearningTarget(self): 
        self.weights = util.Counter()
    
    def getQValue(self,state,actions):
        qValues = []
        for action in actions:
            features = self.getFeatures(state,action)
            qValue = 0
            for key in features :
                qValue += self.weights[key] * features[key]
            qValues.append(qValue)
        return tuple(qValues)

    def updateQ(self,terminate,reward = None,card = None,agent=None):
        if self.mode=='train' and self.lastState != None and self.lastAction != None:
            
            if reward == None :
                reward = self.getReward(terminate)
            state = self.lastState
            action = self.lastAction

            if card == None:
                Property = namedtuple('Property',['terminate','mode'])
                prop = Property(terminate,'throw')
            else:
                Property = namedtuple('Property',['terminate','mode','card','agent'])
                prop = Property(terminate,'take',card,agent)

            nextState = self.getState(prop)
            legalActions = self.getLegalActions(nextState)
            #print (state,action,nextState)
            
            qValues = self.getQValue(nextState,legalActions)
            maxQ = max(qValues)
            difference = (reward + self.discount*maxQ) - self.getQValue(state,[action])[0]
            features = self.getFeatures(state,action)
            for key in features:
                self.weights[key] = self.weights[key] + self.lr*difference*features[key]
    
    def save(self,pickle_name):
        if self.train :
            print ('saving data to ',pickle_name)
            f = open(pickle_name, 'wb')
            cPickle.dump(self.weights, f, protocol=cPickle.HIGHEST_PROTOCOL)
            f.close()

    def load(self,pickle_name):
        print ('This is a weight learning agent')
        if os.path.isfile(pickle_name):
            print ('loading ',pickle_name)
            f = open(pickle_name, 'rb')
            self.weights = cPickle.load(f)
            f.close()
            print (self) 
    ###################################
    ###   Modified function below   ###
    ###################################
    def gameEnd(self,win,lose,score):
        raise NotImplementedError
        Agent.gameEnd(self,win,lose,score)
        
        if win == self.playerNumber :
            score = 100
        else:
            score == -100
        
        self.updateQ(terminate = True, reward = score)

    def getReward(self,terminate):
        raise NotImplementedError
        return 0
     
    def getContent(self):
        raise NotImplementedError
        state = tuple(self.handcard)
        return state
    
    def getFeatures(self,state,action):   
        raise NotImplementedError
                
        feats = util.Counter()
        
        handcard = list(state)
        handcard.remove(action)
        handSet = set(handcard)
       
        feats['手牌數'] = len(handcard)
        feats['雀'] = len([ card for card in handSet if handcard.count(card) == 2])
        feats['刻'] = len([ card for card in handSet if handcard.count(card) == 3])
        feats['槓'] = len([ card for card in handSet if handcard.count(card) == 4])
        
        for card in handSet :
            if int(card/10) < 3 and card % 10 != 0:
                if card %10 < 8 and (card+1 in handSet) and (card+2 in handSet):
                    feats['順'] += 1 
        
        return feats

class SelfLearningAgent(WeightLearningAgent):
    
    def gameEnd(self,win,lose,score):
        Agent.gameEnd(self,win,lose,score)
        if win == self.playerNumber :
            score = 500
        else :
            score = 0
        
        self.updateQ(terminate = True, reward = score)

    def getReward(self,terminate):
        return 0
     
    def getContent(self):
        Content = namedtuple('Content',['handcards','cardsOnBoard','cardsUnSeen'])
        
        handcards = tuple(self.handcard[:]) 
        cardsOnBoard = tuple(self.cardsOnBoard[self.playerNumber][:])
        cardsUnSeen = tuple([ 4 - self.cardOpened.count(i) - self.handcard.count(i) for i in range(34)])
        
        content = Content(handcards,cardsOnBoard,cardsUnSeen)
        return content
    
    def getFeatures(self,state,action):   
        feats = util.Counter()
        content = state.content
        handcard = list(content.handcards)
        cardsOnBoard = list(content.cardsOnBoard)
        
        if isinstance(action,tuple):
            handcard.append(action[1])
            for card in action[0] :
                handcard.remove(card)
            cardsOnBoard.append(action[0])

        elif isinstance(action,int):
            handcard.remove(action)
        elif action != None :
            print ('illegal action in getFeature : ',action)
            raise Exception
        
        handSet = set(handcard)
        cardsUnSeen  = content.cardsUnSeen

        ###############################
        ###   從下面開始找feature   ###
        ###############################
        
        ## 明牌
        for cards in cardsOnBoard :
            if len(cards) == 4:
                feats['槓'] +=1
            elif len(cards) == 3 and len(set(cards)) == 1:
                feats['刻'] +=1
            elif len(cards) == 3 and len(set(cards)) == 3:
                feats['順']+= 1 
            else:
                print ('error :',cards)
                raise Exception
        
        cardsNeeds = [0]*34
        feats['明牌'] = len(cardsOnBoard)
        '''
        ## 丟出牌（action）
        if type(action) != type(tuple()) and action != None and type(action) != type(list()):
            count = cardsUnSeen.count(action)
            ## 依照同張牌（槓刻雀）
            if count == 3:
                feats['可湊組合']+=2
            elif count == 2:
                feats['可湊組合']+=1
            elif count == 1:
                feats['可湊組合']+=0.5
                
            ## 可組成的順
            if action % 10!= 0 and int(action/10) < 3: 
                ## 1
                card = action
                if card % 10 == 1 :
                    feats['可湊組合']+=min(cardsUnSeen[card+1],cardsUnSeen[card+2])
                ## 9
                elif card % 10 == 9 :
                    feats['可湊組合']+=min(cardsUnSeen[card-1],cardsUnSeen[card-2])
                ## 2
                elif card % 10 == 2:
                    ## 1 2 3
                    feats['可湊組合']+=min(cardsUnSeen[card-1],cardsUnSeen[card+1])
                    ## 2 3 4 
                    feats['可湊組合']+=min(cardsUnSeen[card+1],cardsUnSeen[card+2])
                ## 8
                elif card % 10 == 8:
                    ## 7 8 9
                    feats['可湊組合']+=min(cardsUnSeen[card-1],cardsUnSeen[card+1])
                    ## 6 7 8
                    feats['可湊組合']+=min(cardsUnSeen[card-1],cardsUnSeen[card-2])

                ## 3 4 5 6 7
                else:
                    ## a-2 a-1 a
                    feats['可湊組合']+=min(cardsUnSeen[card-1],cardsUnSeen[card-2])
                    ## a-1 a a+1
                    feats['可湊組合']+=min(cardsUnSeen[card-1],cardsUnSeen[card+1])
                    ## a a+1 a+2
                    feats['可湊組合']+=min(cardsUnSeen[card+1],cardsUnSeen[card+2])                    
        else:
            feats['可湊組合'] = 0
        '''
        ## 手牌
        for card in handSet :
            ##############################################################
            ### cardExist :
            ### index :    -2    |    -1    |   0    |    1     |    2  
            ###          card-2  |  card-1  |  card  |  card+1  |  card+2  
            ##############################################################
            cardExist = {i:handcard.count(card+i) for i in range(-2,3)}
            
            ## 廣義孤張判定
            if cardExist[0] == 1 :
                feats['孤張剩牌'] += cardsUnSeen[card]                    
                if int(card/10) == 3 or card%10 ==0 :
                    feats['孤張'] += 1
                elif card % 10 == 1 :
                    ## 手牌沒有2 3
                    if not cardExist[1] and not cardExist[2]:
                        feats['孤張'] += 1
                    ## 手牌 有2但3以被拿完 或 有3但2以被拿完
                    elif (not cardExist[1] and not cardsUnSeen[card+1]) or (not cardExist[2] and not cardsUnSeen[card+2]):
                        feats['孤張'] += 1
                elif card%10 == 9 :
                    ## 手牌沒有7 8
                    if not cardExist[-1] and not cardExist[-2]:
                        feats['孤張'] += 1
                    ## 手牌 有7但8以被拿完 或 有8但7以被拿完
                    elif (not cardExist[-1] and not cardsUnSeen[card-1]) or (not cardExist[-2] and not cardsUnSeen[card-2]):
                        feats['孤張'] += 1
                elif card%10 == 2:
                    ## 手牌沒有1 4
                    if not cardExist[-1] and not cardExist[2] : 
                        ## 沒有3
                        if not cardExist[1] :
                            feats['孤張'] += 1
                        ## 1 4 已被拿完
                        elif not cardsUnSeen[card-1] and not cardsUnSeen[card+2]:
                            feats['孤張'] += 1
                    ## 有1或4沒3,但3已被拿完
                    elif (cardExist[-1] or cardExist[2]) and not cardExist[1] and not cardsUnSeen[card+1]: 
                         feats['孤張'] += 1
                elif card%10 == 8:
                    ## 手牌沒有6 9
                    if not cardExist[-2] and not cardExist[1]:
                        ## 手牌沒有 7
                        if not cardExist[-1]:
                            feats['孤張'] += 1
                        ## 6 9 已被拿完
                        elif not cardsUnSeen[card-2] and not cardsUnSeen[card+1]:
                            feats['孤張'] += 1
                    ## 有6或9沒7,但7已被拿完
                    elif (cardExist[-2] or cardExist[1]) and not cardExist[-1]and not cardsUnSeen[card-1]: 
                         feats['孤張'] += 1
                else: ## 3 4 5 6 7  
                    if not cardExist[-2] and not cardExist[-1] and not cardExist[1] and not cardExist[2]:
                        feats['孤張'] += 1
                    else:
                        combination = [cardExist[i]*cardExist[i+1]*cardExist[i+2] for i in range(-2,1)]
                        if sum(combination) == 0:
                            found = False
                            if (cardExist[-2] and cardsUnSeen[card-1]) or (cardExist[-1] and cardsUnSeen[card-2]):
                                found = True
                            elif (cardExist[-1] and cardsUnSeen[card+1]) or (cardExist[1] and cardsUnSeen[card-1]):
                                found = True
                            elif (cardExist[1] and cardsUnSeen[card+2]) or (cardExist[2] and cardsUnSeen[card+1]):
                                found = True
                            if not found :
                                feats['孤張'] += 1
            if cardExist[0] == 2:     
                if cardsUnSeen[card]:
                    feats['成刻對'] += cardsUnSeen[card]
                else :
                    feats['不成刻對'] += 1
            ## 檢查刻 
            if cardExist[0] == 3:
                feats['刻'] += 1
            ## 檢查槓
            if cardExist[0] == 4:
                feats['槓'] += 1 
            ### 檢查順
            if int(card/10) < 3 and card % 10 != 0:
                if card %10 < 8 and cardExist[1] and cardExist[2]:
                    feats['順'] += 1 
                ## 邊張12
                if  card % 10 == 1 and cardExist[1] and not cardExist[2]:
                    feats['雙牌組合'] += cardsUnSeen[card+2]
                ## 邊張89
                if  card % 10 == 9 and cardExist[-1] and not cardExist[-2]:
                    feats['雙牌組合'] += cardsUnSeen[card-2]
                ## 兩面
                if  card % 10 > 1 and card % 10 < 8 and cardExist[1]:
                    if not cardExist[-1] :
                        feats['雙牌組合'] += cardsUnSeen[card-1]
                    if not cardExist[2] :
                        feats['雙牌組合'] += cardsUnSeen[card+2]
                ## 坎張
                if  card%10 < 8 and not cardExist[1] and cardExist[2]:
                    feats['雙牌組合'] += cardsUnSeen[card+1]
                        
        #feats['有效牌'] = sum(i*j for i,j in zip(cardsUnSeen, cardsNeeds))
        
        return feats

class ScoreLearningAgent(SelfLearningAgent):
    def gameEnd(self,win,lose,score):
        Agent.gameEnd(self,win,lose,score)
        
        '''
        if score != None:
            if score < 0 :
                score = 0
        '''
        if win == self.playerNumber :
            score = 500
        else :
            score = 0
        
        self.updateQ(terminate = True, reward = score)

    def getReward(self,terminate):
        return 0
     
    def getContent(self):
        Content = namedtuple('Content',['handcards','cardsOnBoard','cardsUnSeen','cardOpened'])
        
        handcards = tuple(self.handcard[:]) 
        cardsOnBoard = tuple(self.cardsOnBoard[self.playerNumber][:])
        cardsUnSeen = tuple([ 4 - self.cardOpened.count(i) - self.handcard.count(i) for i in range(34)])
        cardOpened = tuple(self.cardOpened[:])
        
        content = Content(handcards,cardsOnBoard,cardsUnSeen,cardOpened)
        return content
    
    def getFeatures(self,state,action):

        feats = SelfLearningAgent.getFeatures(self,state,action)
        
        content = state.content
        handcard = list(content.handcards)
        cardsOnBoard = list(content.cardsOnBoard)
        
        if isinstance(action,tuple):
            handcard.append(action[1])
            for card in action[0] :
                handcard.remove(card)
            cardsOnBoard.append(action[0])

        elif isinstance(action,int):
            handcard.remove(action)
        elif action != None :
            print ('illegal action in getFeature : ',action)
            raise Exception
        
        handSet = set(handcard)
        cardsUnSeen  = content.cardsUnSeen
        enemyCardsOnBoard = (content.cardOpened[i] for i in range(4) if i != self.playerNumber )
        
        ###############################
        ###   從下面開始找feature   ###
        ###############################
         
        '''
        ### 檢查明牌
        for cards in cardsOnBoard :
            if len(cards) == 3 and len(set(cards)) == 1 :
                card = cards[0]
                if card == 0 or card == 10 or card == 20:
                    feats['三元刻'] += 1
                elif card >=30 and card <=33: 
                    feats['風刻'] += 1
            elif len(cards)==4 and len(set(cards)) == 1:
                card = cards[0]
                if card == 0 or card == 10 or card == 20:
                    feats['三元槓'] += 1
                elif card >=30 and card <= 33:
                    feats['風槓'] += 1
            elif len(cards)==3 and len(set(cards))==3:
        '''     
        ### 檢查手牌
        for card in handSet :
            count = handcard.count(card)
            ''' 
            if count == 2:
                if card == 0 or card ==10 or card == 20:
                    feats['三元對'] += 1
                elif card >=30 and card <=33: 
                    feats['風對'] += 1
            '''
            if count == 3 :
                feats['暗刻'] +=1
                '''
                if card == 0 or card == 10 or card == 20:
                    feats['三元刻'] += 1
                elif card >=30 and card <=33: 
                    feats['風刻'] += 1
                '''
            '''
            elif count == 4 :
                if card == 0 or card == 10 or card == 20:
                    feats['三元槓'] += 1
                elif card >=30 and card <= 33:
                    feats['風槓'] += 1
            '''
        '''
        feats['三元牌'] = feats['三元槓']+feats['三元刻']
        feats['風牌'] = feats['風槓']+feats['風刻']
        feats['字'] =feats['三元牌'] +feats['風牌']+feats['三元對'] +feats['風對']
        '''
        return feats
