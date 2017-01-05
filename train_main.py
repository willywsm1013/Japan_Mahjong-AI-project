from Table import Table
from SimpleAgent import *
from getScore import getScore
from learningAgent import *
import sys
import operator
from six.moves import cPickle
import matplotlib.pyplot as plt
Verbose = False
UI = False
plotQ = False

decreaseEpsilon = True
train = False

table = Table(False)
winRecord = [0]*4
loseRecord = [0]*4
repeat = 1000.0
rounds = 1000
data = []
scores = [0]*4
Round = 0
pickle = 'selfLearning_ver4'
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
        if scoreBoard != None :
            for i in range(len(scores)):
                scores[i] += scoreBoard[i]
        if winner != None:
            win[winner]+=1
        if loser != None:
            lose[loser]+=1
        
    return win[playerNumber]
'''
def linearDecay(n,time,decayPeriod,minimum):
    period = int(time / daceyPeriod)
    return 
'''
try :
    table.addAgent(RandomAgent(0))
    table.addAgent(RandomAgent(1))
    table.addAgent(RandomAgent(2))
    if train :
        table.addAgent(SelfLearningAgent(player_number = 3,
                                         epsilon = 1,
                                         alpha = 1e-5,
                                         mode = 'train',
                                         pickle_name=pickle,
                                         lr_decay_fn = linearDecay(decayRate = 5e-8,minimum=1e-7,init = True)
                                        ))
        maxWin = testing(table,3,rounds)
    else :
        table.addAgent(SelfLearningAgent(3,mode = 'test',pickle_name=pickle))
    
    maxWin = 0
    for time in range(int(repeat)):
        Round += 1.0
        print ('Round :',Round)

        table.newGame()
        table.deal()
        
        winner,loser,scoreBoard= table.gameStart(verbose=Verbose,UI=UI)
        if scoreBoard != None :
            for i in range(len(scores)):
                scores[i] += scoreBoard[i]
            print ('分數:',scores)
            print ('平均分數:',[scores[i]/Round for i in range(4)])
            print (scoreBoard)
            assert sum(scoreBoard) == 0
            #input()
        if winner != None:
            winRecord[winner]+=1
        if loser != None:
            loseRecord[loser]+=1
        print ('**************************')
        if train :
            if (time+1) % 10000 == 0:
                table.gameEnd()
                testWin = testing(table,3,rounds)
                print ('testing win games : ',testWin)
                #input()
                if testWin > maxWin :
                    print ('Saving...')
                    table.gameEnd(save = True, player = 3,pickle_name = pickle)
                    maxWin = testWin
                    #input()
                if decreaseEpsilon:
                    table.agents[3].setEpsilon(1-testWin/rounds)
            if (time+1) % 1000 ==0:
                table.agents[3].lrDecay()
            else :
                table.gameEnd()
        if plotQ :
            qValue = table.agents[3].recordQ
            plt.plot(qValue)
            plt.ylabel('Q value')

    print ('胡:', [winRecord[i]/Round for i in range(4)])
    print ('放槍:',[loseRecord[i]/Round for i in range(4)])
    print ('分數:',scores)
    print ('平均分數:',[scores[i]/Round for i in range(4)])
    for data in Table.loseReason[3]:
        print (data)

except KeyboardInterrupt:
    print ('胡:', [winRecord[i]/Round for i in range(4)])
    print ('放槍:',[loseRecord[i]/Round for i in range(4)])
    print ('分數:',scoreBoard)
    print ('平均分數:',[scores[i]/Round for i in range(4)])
    for data in Table.loseReason[3]:
        print (data)


