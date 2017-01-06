from Table import Table
from SimpleAgent import *
from getScore import getScore
from learningAgent import *
import sys,threading
import operator
from six.moves import cPickle
import matplotlib.pyplot as plt
import time as timer

Verbose = False
UI = False
plotQ = False

decreaseEpsilon = False
train = False

table = Table(False)
winRecord = [0]*4
loseRecord = [0]*4
repeat = 100000.0
rounds = 1000
data = []
scores = [0]*4
Round = 0
pickle = 'selfLearning（槓）（刻）（順）（明牌）（孤張）（雀）'

#pickle = 'selfLearningNoDecrease0.8'
maxWin = 0

def linearDecay(value=None,decayRate=None,minimum=None,init = False):
    if init :
        linearDecay.init = True
        linearDecay.rate = decayRate
        linearDecay.minimum = minimum
    else :
        if not linearDecay.init:
            raise Exception
        v = value - linearDecay.rate
        return max(v,linearDecay.minimun)

def exponentialDecay(value = None):
    decayRate = 0.95
    minimum = 1e-20
    v = value * decayRate
    return max(v,minimum)

def testing(table,playerNumber,rounds):
    print ('testing...')
    testTable = Table(False)
    testTable.addAgent(RandomAgent(0))
    testTable.addAgent(RandomAgent(1))
    testTable.addAgent(RandomAgent(2))
    
    agent = SelfLearningAgent(3,mode = 'test')
    agent.weights = table.agents[playerNumber].weights.copy() 
    testTable.addAgent(agent)
    
    win = [0]*4
    lose = [0]*4
    for time in range(rounds):
        testTable.newGame()
        testTable.deal()
        
        winner,loser,scoreBoard= testTable.gameStart(verbose=Verbose,UI=UI)
        if winner != None:
            win[winner]+=1
        if loser != None:
            lose[loser]+=1
        
    return win[playerNumber]

winRate = []
winCounts = []
try :
    table.addAgent(RandomAgent(0))
    table.addAgent(RandomAgent(1))
    table.addAgent(RandomAgent(2))
    if train :
        table.addAgent(SelfLearningAgent(player_number = 3,
                                         discount = 0.8,
                                         epsilon = 0.5,
                                         alpha = 0.0001,
                                         mode = 'train',
                                         pickle_name=pickle,
                                         lr_decay_fn = exponentialDecay
                                        ))
        maxWin = testing(table,3,rounds)
        if decreaseEpsilon:
            table.agents[3].setEpsilon(1-maxWin/rounds)

        winRate.append(maxWin)
    else :
        table.addAgent(SelfLearningAgent(3,mode = 'test',pickle_name=pickle))
    
    maxWin = 0
    for time in range(int(repeat)):
        Round += 1.0
        if Verbose:
            print ('Round :',Round,', win rate for recently 100 games : ',sum(winCounts)/100)
        else :
            print ('Round :',Round,', win rate for recently 100 games : ',sum(winCounts)/100,end = '\r')

        table.newGame()
        table.deal()
        
        winner,loser,scoreBoard= table.gameStart(verbose=Verbose,UI=UI)
        if scoreBoard != None :
            for i in range(len(scores)):
                scores[i] += scoreBoard[i]
            if Verbose:
                print ('分數:',scores)
                print ('平均分數:',[scores[i]/Round for i in range(4)])
                assert sum(scoreBoard) == 0
            #input()
        winCounts.append(int(winner == 3))
        if len(winCounts) > 100:
            winCounts.pop(0)
        
        if winner != None:
            winRecord[winner]+=1
        if loser != None:
            loseRecord[loser]+=1
        if Verbose:
            print ('**************************')
        if train :
            if (time+1) % 10000 == 0:
                table.gameEnd()
                testWin = testing(table,3,rounds)
                winRate.append(testWin)
                print ('testing win games : ',testWin)
                #input()
                if testWin > maxWin :
                    print ('Saving...')
                    table.gameEnd(save = True, player = 3,pickle_name = pickle)
                    maxWin = testWin
                    #input()
                if decreaseEpsilon:
                    table.agents[3].setEpsilon(1-(time+1)/100000)
            else :
                table.gameEnd()

            '''
            if (time+1) % 1000 ==0 and decreaseEpsilon:
                table.agents[3].lrDecay()
            '''
        if plotQ :
            qValue = table.agents[3].recordQ             
            #plt.ion()
            plt.plot(qValue)
            plt.ylabel('Q value')
            plt.show()
    print ('胡:', [winRecord[i]/Round for i in range(4)])
    print ('放槍:',[loseRecord[i]/Round for i in range(4)])
    print ('分數:',scores)
    print ('平均分數:',[scores[i]/Round for i in range(4)])
    print ('勝率紀錄:',winRate)
    for data in Table.loseReason[3]:
        print (data)
    if plotQ :
        plt.plot(winRate)
        plt.ylabel('%')
        plt.xlabel('per 10000 training')
        plt.show()

except KeyboardInterrupt:
    print ('胡:', [winRecord[i]/Round for i in range(4)])
    print ('放槍:',[loseRecord[i]/Round for i in range(4)])
    print ('分數:',scoreBoard)
    print ('平均分數:',[scores[i]/Round for i in range(4)])
    for data in Table.loseReason[3]:
        print (data)


