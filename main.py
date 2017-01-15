from Table import Table
from SimpleAgent import *
from evalScore import evalScore
import sys
import operator
Verbose = False
UI = False  


table = Table(True)
winRecord = [0]*4
loseRecord = [0]*4
repeat = 10000.0
data = []
scores = [0]*4
Round = 0
try :
    for time in range(int(repeat)):
        Round += 1.0
        print ('Round :',time)
        table.newGame()
        for i in range(3):
            table.addAgent(OneStepAgent(i))
        table.addAgent(ValueAgent(3))
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
        if Verbose:
            if loser == 3:
                input()
    print ('胡:', [winRecord[i]/Round for i in range(4)])
    print ('放槍:',[loseRecord[i]/Round for i in range(4)])
    print ('分數:',scoreBoard)
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


