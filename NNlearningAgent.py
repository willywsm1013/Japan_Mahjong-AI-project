from learningAgent import *
from data_util import DataSet
import numpy as np
import tensorflow as tf

#############################################
###   basic class for NN learning Agent   ###
#############################################
class NNLearningAgent(QLearningAgent):
    def __init__(self,player_number,params,mode,model=None):
        self.model = model 
        QLearningAgent.__init__(self,player_number,params,mode) 
        self.dataSet = DataSet(params.batch_size,params.data_set_max_size,params.data_set_name)
    
    def setLearningTarget(self):
        pass

    def __str__(self):
        information = "Agent : NNLearningAgent\n"
        information += "Model name : " + self.model.name + "\n"
        information += "Status : " + self.mode + "\n"
        return information
    
    def save(self,pickle_name = None):
        if self.mode == 'train' :
            if pickle_name == None :
                params = self.params
                pickle_name = params.save_dir
            print ('Saving model to ',pikckle_name)
            self.model.save(pickle_name)
        else:
            print('Model cannot be saved in testing mode.')

    def load(self,pickle_name= None):
        if pickle_name == None:
            params = self.params
            pickle_name = params.load_dir
        print ('Loading model from ',pickle_name)
        self.model.load(pickle_name)
    
    def getQValue(self,state,actions):
        
        ####
        inputs = self.getInputs(state,actions)
        ####

        return self.model.test(inputs)

    def updateQ(self,terminate,reward = None,card = None, agent=None):
        
        if self.mode == 'train' and self.lastState != None and self.lastAction != None:
            if reward == None :
                reward = self.getReward(terminate)
            state = self.lastState
            action = self.lastAction
            
            prop = {}
            if card == None:  ## 丟牌的時候
                prop['terminate'] = terminate
                prop['mode'] = 'throw'
            else:             ## 拿牌的時候（判斷吃碰槓）
                prop['terminate'] = terminate
                prop['mode'] = 'throw'
                prop['card'] = card
                prop['agent'] = agent

            nextState = self.getState(prop)
            legalActions = self.getLegalActions(nextState)
            
            ####
            nextInputs = self.getInputs(nextState,legalActions)
            if not terminate:
                currentInput = self.getInputs(state,[action])[0]
                self.dataSet.add([currentInput,reward,nextInputs])
            else:
                assert legalActions == (None,)
                self.dataSet.add([nextInputs[0],reward,None])
            ####
            self.model.train(self.dataSet)

    #----------------------------#
    #   modify functions below   #
    #----------------------------#
    
    def gameEnd(self,win,lose,score):
        raise NotImplementedError
                         
    def getReward(self,terminate):
        raise NotImplementedError() 
        
    def getContent(self):
        raise NotImplementedError() 
    
    def getInputs(self,state,actions):
        raise NotImplementedError() 

class NNSelfLearningAgent(NNLearningAgent):
    def gameEnd(self,win,lose,score):
        Agent.gameEnd(self,win,lose,score)
        if win == self.playerNumber :
            score = 500
        else :
            score = 0
        
        self.updateQ(terminate = False)
        self.updateQ(terminate = True, reward = score)
            
    def getReward(self,terminate = False):
        return 0
    
    def getContent(self):
        content = {}
        content['handcards'] = tuple(self.handcard[:]) 
        content['cardsOnBoard'] = tuple(self.cardsOnBoard[self.playerNumber][:])
        content['cardsUnSeen'] = tuple([ 4 - self.cardOpened.count(i) - self.handcard.count(i) for i in range(34)])
        return content
    
    def getInputs(self,state,actions):
        inputs = []
        
        content = state['content']

        for action in actions:
            handcard = list(content['handcards'])
            cardsOnBoard = list(content['cardsOnBoard'])
                        
            if isinstance(action,tuple):
                handcard.append(action[1])
                #print ('handcard:',handcard)
                for card in action[0] :
                    #print ('card:',card)
                    handcard.remove(card)
                cardsOnBoard.append(action[0])

            elif isinstance(action,int):
                handcard.remove(action)
            elif action != None :
                print ('illegal action in getFeature : ',action)
                raise Exception
            ''' 
            handSet = set(handcard)
            cardsUnSeen  = content['cardsUnSeen']
            '''
            
            cards = np.zeros((34,),dtype = 'float32')
            for card in handcard:
                cards[card] += 1
                assert cards[card] <= 4
            for comb in cardsOnBoard:
                for card in comb:
                    cards[card] += 1
                    assert cards[card] <= 4
            
            inputs.append(cards)
        return inputs

