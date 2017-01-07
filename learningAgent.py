#-*- coding: utf-8 -*-　
from Agent import *
import util 
import random
import os
from six.moves import cPickle

class QLearningAgent(Agent):
    
    def __init__(self,player_number,epsilon=0.5,discount=0.8,alpha=1e-4,mode='test',pickle_name = None,lr_decay_fn = None):
        Agent.__init__(self,player_number)
        self.epsilon = epsilon
        self.discount = discount
        self.alpha = alpha
        self.setLearningTarget()
        self.lr_decay = lr_decay_fn
        print (lr_decay_fn)
        if mode == 'train':
            self.train = True
        elif mode == 'test':
            self.train = False
        else:
            print ('no mode \'',mode,'\' for QlearningAgent')
            raise Exception
        
        self.reset()
        if pickle_name != None:
            self.load(pickle_name)
    
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
        
        self.updateQ(terminate = False)
        ### 取得legal actions
        currentState = self.getState()
        legalActions = self.getLegalActions(terminate = False,mode = 'take',card = card, agent = agentNum)
        
        if self.train and util.flipCoin(self.epsilon) :
            action = random.choice(legalActions)
        else :
            q = [self.getQValue(currentState,action) for action in legalActions]
            maxQ = max(q)
            self.recordQ.append(maxQ)
            maxActions = [ legalActions[i] for i in range(len(legalActions)) if q[i] == maxQ]
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
            
    def takeActionByQ(self):
        currentState = self.getState()
        
        if self.train and util.flipCoin(self.epsilon) :
            throw = random.choice(self.handcard)
        else :
            legalActions = self.getLegalActions()
            q = [self.getQValue(currentState,action) for action in legalActions]
            maxQ = max(q)
            self.recordQ.append(maxQ)
            maxActions = [ legalActions[i] for i in range(len(legalActions)) if q[i] == maxQ]
            throw = random.choice(maxActions)
         
        self.handcard.remove(throw)
        
        self.lastState = currentState
        self.lastAction = throw
        
        return throw
    
    def getLegalActions(self,terminate = False,mode = 'throw',card = None, agent=None):
        if terminate:
            return None
        if mode == 'throw':
            return tuple(set(self.handcard))
        elif mode == 'take':
            assert card !=None
            legalActions = [None]
            ## 檢查刻
            if self.handcard.count(card) == 2:
                legalActions.append(((card,card,card),card))
            ## 檢查槓
            if self.handcard.count(card) == 3:
                legalActions.append(((card,card,card,card),card))

            ## 檢查順
            sub = self.playerNumber - agent
            if (sub == 1 or sub == -3) and int(card/10) < 3 and card%10 != 0 :
                if card % 10 < 8 and ((card+1) in self.handcard) and ((card+2) in self.handcard):
                    legalActions.append(((card,card+1,card+2),card))
                if card % 10 !=1 and card%10 != 9 and ((card-1) in self.handcard) and ((card+1) in self.handcard):
                    legalActions.append(((card-1,card,card+1),card))
                if card % 10 > 2 and ((card-1) in self.handcard) and ((card-2) in self.handcard):
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
        print ('learning rate :',self.alpha,' -> ',end='')
        if self.lr_decay != None:
            self.alpha = self.lr_decay(self.alpha)
        print (self.alpha)
    
    #########################################
    ###   don't modified function above   ###
    #########################################
    def gameEnd(self,win,lose,score):
        Agent.gameEnd(self,score)
        self.updateQ(terminate = True, reward = score)

    def setLearningTarget(self): 
        self.qValues = util.Counter()
            
    def updateQ(self,terminate,reward = None):
        if self.train :
            if reward == None :
                reward = self.getReward()
            state = self.lastState
            action = self.lastAction
            nextState = self.getState()

            legalActions = self.getLegalActions(terminate)
            
            maxQ = 0
            if legalActions :
                maxQ = self.discount * max([self.getQValue(nextState,a) for a in legalActions])
            q = self.getQValue(state,action)
            self.qValues[(state,action)] = q + self.alpha*(reward + maxQ - q)
    
        
    def getReward(self):
        return 0
    
    def getQValue(self,state,action):
        return self.qValues[(state,action)]
    
    def getState(self):
        state = self.handcard + sum(self.cardsOnBoard[self.playerNumber],[])
        state.sort()
        return tuple(state) 
    
    def save(self,pickle_name):
        print ('saving data to ',pikckle_name)
        if self.train :
            f = open(pickle_name, 'wb')
            cPickle.dump(self.qValues, f, protocol=cPickle.HIGHEST_PROTOCOL)
            f.close()

    def load(self,pickle_name):
        print ('loading ',pickle_name)
        if os.path.isfile(pickle_name):
            f = open(pickle_name, 'rb')
            self.qValues = cPickle.load(f)
            f.close()
   
class WeightLearningAgent(QLearningAgent):
    def setLearningTarget(self): 
        self.weights = util.Counter()
    
    def getQValue(self,state,action):
        
        features = self.getFeatures(state,action)
        qValue = 0
        for key in features :
            qValue += self.weights[key] * features[key]
        return qValue

    def updateQ(self,terminate,reward = None):
        if self.train and self.lastState != None and self.lastAction != None:
            
            if reward == None :
                reward = self.getReward(terminate)
            elif reward < 0:
                reward -= 100
            state = self.lastState
            action = self.lastAction
            nextState = self.getState()
            #print (state,action,nextState)
            legalActions = self.getLegalActions(terminate)
            
            maxQ = 0
            if legalActions :
                maxQ = max([self.getQValue(nextState,a) for a in legalActions])
            difference = (reward + self.discount*maxQ) - self.getQValue(state,action)
            features = self.getFeatures(state,action)
            for key in features:
                self.weights[key] = self.weights[key] + self.alpha*difference*features[key]
    
    def save(self,pickle_name):
        if self.train :
            print ('saving data to ',pickle_name)
            f = open(pickle_name, 'wb')
            cPickle.dump(self.weights, f, protocol=cPickle.HIGHEST_PROTOCOL)
            f.close()
            self.printWeight()

    def load(self,pickle_name):
        print ('This is a weight learning agent')
        if os.path.isfile(pickle_name):
            print ('loading ',pickle_name)
            f = open(pickle_name, 'rb')
            self.weights = cPickle.load(f)
            f.close()
            self.printWeight()
    
    def printWeight(self):
        for key in self.weights:
            print (key,':',self.weights[key])
    ###################################
    ###   Modified function below   ###
    ###################################
    def gameEnd(self,win,lose,score):
        Agent.gameEnd(self,win,lose,score)
        
        if win == self.playerNumber :
            score = 100
        else:
            score == -100
        
        self.updateQ(terminate = True, reward = score)

    def getReward(self,terminate):
        return 0
     
    def getState(self):
        state = tuple(self.handcard)
        return state
    
    def getFeatures(self,state,action):   
                
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
     
    def getState(self):
        cardsUnSeen = [ 4 - self.cardOpened.count(i) - self.handcard.count(i) for i in range(34)]
        state = [tuple(self.handcard),tuple(self.cardsOnBoard[self.playerNumber]),tuple(cardsUnSeen)]
        return state
    
    def getFeatures(self,state,action):   
                
        feats = util.Counter()
        handcard = list(state[0])
        if type(action) == type(tuple()):
            handcard.append(action[1])
            for card in action[0] :
                handcard.remove(card)
            cardsOnBoard = list(state[1])
            cardsOnBoard.append(list(action[0]))
            cardsOnBoard = tuple(cardsOnBoard)

        elif action != None and type(action) == type(int()):
            handcard.remove(action)
            cardsOnBoard = state[1]
        elif action == None:
            cardsOnBoard = state[1]
        else :
            print ('unlegal action in getFeature : ',action)
            raise Exception
        
        handSet = set(handcard)
        cardsUnSeen  = state [2]

        ###############################
        ###   從下面開始找feature   ###
        ###############################
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
        
        for card in handSet :
            ##############################################################
            ### cardExist :
            ### index :    -2    |    -1    |   0    |    1     |    2  
            ###          card-2  |  card-1  |  card  |  card+1  |  card+2  
            ##############################################################
            cardExist = {i:handcard.count(card+i) for i in range(-2,3)}
            
            ## 廣義孤張判定
            if cardExist[0] == 1 :
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
            #feats['複製'] += cardsUnSeen[card]                    
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

