from Table import Table
from SimpleAgent import *
from getScore import getScore
from learningAgent import *
import sys,threading
import operator
from six.moves import cPickle
import matplotlib.pyplot as plt
import time as timer
import math
import argparse



##########################
###   command Parser   ###
##########################
parser = argparse.ArgumentParser(description='')

parser.add_argument('-train',"--train", action='store_true', help = "open training mode")
parser.add_argument('-test',"--test", action='store_true', help = "open testing mode")
parser.add_argument('-r',"--repeat", type=float,dest = "repeat", default = 1, help = "training or testing times[1]")
parser.add_argument('-v','--verbose',action='store_true',help='print information')
parser.add_argument('-ui','--UI',action='store_true',help='open user interface')
parser.add_argument('-pw','--print_weight',action='store_true',help='print weight of learningAgent')
parser.add_argument('-dlr','--decrease_learning_rate',action='store_true',help='decrease learning rate')
parser.add_argument('-dep','--decrease_epsilon',action='store_true',help='decrease epsilon')


args = parser.parse_args()

Verbose = args.verbose
UI = args.UI

train = args.train
test = args.test

repeat = args.repeat
print_weight = args.print_weight

decreaseEpsilon = args.decrease_epsilon
decreaseLearningRate = args.decrease_learning_rate

plotQ = False
rounds = 1000

pickle = 'selfLearning（槓）（刻）（順）（明牌）（廣義孤張）（成刻對）（不成刻對）（雙牌）'

#########################
###   program start   ###
#########################
if print_weight:
    agent = SelfLearningAgent(0,pickle_name=pickle)
    sys.exit()

table = Table(False)
winRecord = [0]*4
loseRecord = [0]*4
data = []
scores = [0]*4
Round = 0

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
    decayRate = 0.9
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
train_Q = []
try :
    table.addAgent(RandomAgent(0))
    table.addAgent(RandomAgent(1))
    table.addAgent(RandomAgent(2))
    if train :
        epsilon = 0.5
        if decreaseEpsilon :
            epsilon = 1
        table.addAgent(SelfLearningAgent(player_number = 3,
                                         discount = 0.8,
                                         epsilon = epsilon,
                                         alpha = 0.0001,
                                         mode = 'train',
                                         pickle_name=pickle,
                                         lr_decay_fn = exponentialDecay
                                        ))
        maxWin = testing(table,3,rounds)
        winRate.append(maxWin)
    elif test:
        table.addAgent(SelfLearningAgent(3,mode = 'test',pickle_name=pickle))
    else :
        print ('please use -train or -test flags')
        sys.exit()
    
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
            '''
            qValue=table.agents[3].recordQ
            train_Q.append(sum(qValue)/len(qValue)+1)
            if plotQ and (time+1) % 1000 == 0:
                plt.plot(train_Q)
                plt.ylabel('Q value')
                plt.show()
            '''
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

            if (time+1) % 1000 ==0 and decreaseLearningRate:
                table.agents[3].lrDecay()
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


