from Table import Table
from SimpleAgent import *
from learningAgent import *
import sys,threading
import operator
from six.moves import cPickle
import matplotlib.pyplot as plt
import time as timer
import math
import argparse
from collections import namedtuple


##########################
###   command Parser   ###
##########################
parser = argparse.ArgumentParser()

# action
parser.add_argument('-m','--mode',choices=['train','test'])

parser.add_argument('-pw','--print_weight', action='store_true', help = 'print weight of learningAgent')
# directory
parser.add_argument('--load_dir',default='')
# training options
parser.add_argument('-dis','--discount',type=float,default=0.8,help='setting discount[0.8]')
parser.add_argument('-lr','--learning_rate',type=float,default=1e-5,help='setting learning rate[1e-5]')
parser.add_argument('-ep','--epsilon',type=float,default=0.5,help='setting epsilon')
parser.add_argument('-dlr','--decrease_learning_rate',action='store_true',help='decrease learning rate')
parser.add_argument('-dep','--decrease_epsilon',action='store_true',help='decrease epsilon')

parser.add_argument('-r',"--repeat", type=float, default = 1, help = "training or testing times[1]")
parser.add_argument('-v','--verbose',action='store_true',help='print information')
parser.add_argument('-ui','--UI',action='store_true',help='open user interface')
parser.add_argument('-pq','--plot_q',action='store_true',help='plot Q value')
parser.add_argument('-e','--enemy',default='random',choices=['random','onestep','selflearn'],help='enemy type[random]')
parser.add_argument('-le','--load_enemy',default=None,help='enemy weights file')
parser.add_argument('-t','--target',default='win_rate',choices=['win_rate','average_score','best_score'],help='learning target[win_rate]')

args = parser.parse_args()

Verbose = args.verbose
UI = args.UI


repeat = args.repeat
print_weight = args.print_weight

learningRate=args.learning_rate
epsilon=args.epsilon
decreaseEpsilon = args.decrease_epsilon
decreaseLearningRate = args.decrease_learning_rate

enemyType = args.enemy
plotQ = args.plot_q

target = args.target
rounds = 1000

pickle = './save/scorelearn/scoreLearning（暗刻）'

##  create params  ##
params_dict = vars(args)
params_class = namedtuple('params_class', params_dict.keys())
params = params_class(**params_dict)

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
def getEnemy(number,enemy_type):
    if enemy_type == 'random':
        return RandomAgent(number)
    elif enemy_type == 'onestep':
        return OneStepAgent(number)
    elif enemy_type == 'selflearn':
        return SelfLearningAgent(number,mode = 'test',pickle_name=pickle)
    else:
        print ('no ',enemy_type,' agent')
        raise Exception

def testing(table,playerNumber,rounds):
    
    print ('testing...')
    testTable = Table(False)
    for i in range(3):
        testTable.addAgent(getEnemy(i,'random'))
    
    agent = ScoreLearningAgent(3,params,mode = 'test')
    agent.weights = table.agents[playerNumber].weights.copy() 
    testTable.addAgent(agent)
    win = [0]*4
    lose = [0]*4
    scores = [0]*4
    for time in range(rounds):
        print ('testing...',time,end='\r')
        testTable.newGame()
        testTable.deal()
        
        winner,loser,scoreBoard= testTable.gameStart(verbose=Verbose,UI=UI)
        if winner != None:
            win[winner]+=1
        if loser != None:
            lose[loser]+=1
        if scoreBoard != None :
            for i in range(4): scores[i]+=scoreBoard[i]
    print ('testing win games : ',win[playerNumber])
    print ('testing lose games : ',lose[playerNumber])
    print ('testing scores : ',scores)

    return win[playerNumber],lose[playerNumber],scores

keeps = []
winCounts = []
train_Q = []
try :
    for i in range(3):
        table.addAgent(getEnemy(i,enemyType))
    
    if args.mode == 'train' :
        table.addAgent(ScoreLearningAgent(3,params,mode = 'train'))
        testWin,testLose,testScores = testing(table,3,rounds)
        if target == 'win_rate':
            keep = testWin
        elif target == 'average_score':
            keep = testScores[3]
        keeps.append(keep)
    elif args.mode == 'test' :
        table.addAgent(ScoreLearningAgent(3,params,mode= 'test'))
    else :
        print ('please use -train or -test flags')
        sys.exit()
    
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
        if args.mode == 'train' :            
                        
            if (time+1) % 10000 == 0:
                table.gameEnd()
                
                print ('====================')
                print (table.agents[3])
                print ('====================')

                testWin,testLose,testScores = testing(table,3,rounds)
                if target == 'win_rate' and testWin > keep:
                    keeps.append(testWin)
                    print ('Saving...')
                    table.gameEnd(save = True, player = 3,pickle_name = pickle)
                    keep = testWin

                elif target == 'average_score' and testScores[3] > keep:
                    keeps.append(testScores[3])
                    print ('Saving...')
                    table.gameEnd(save = True, player = 3,pickle_name = pickle)
                    keep = testScores[3]

                if decreaseEpsilon:
                    table.agents[3].setEpsilon(1-(time+1)/100000)
               
            else :
                table.gameEnd()

            if (time+1) % 1000 ==0 and decreaseLearningRate:
                table.agents[3].lrDecay()
        if plotQ :
            qValue=table.agents[3].recordQ
            plt.plot(qValue)
            plt.ylabel('Q value')
            plt.show()

    print ('胡:', [winRecord[i]/Round for i in range(4)])
    print ('放槍:',[loseRecord[i]/Round for i in range(4)])
    print ('分數:',scores)
    print ('平均分數:',[scores[i]/Round for i in range(4)])
    if target == 'win_rate':
        print ('勝率紀錄:',keeps)
    elif target == 'average_score':
        print ('平均得分:',[i/rounds for i in keeps])
        
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


