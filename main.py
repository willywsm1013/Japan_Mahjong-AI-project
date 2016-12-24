from Table import Table
from SimpleAgent import *
import sys
Verbose = False
UI = False


table = Table(True)
winRecord = [0]*4
loseRecord = [0]*4
repeat = 2000.0
data = []
Round = 0
try :
    for time in range(int(repeat)):
        print ('Round :',time)
        table.newGame()
        for i in range(3):
            table.addAgent(OneStepAgent(i))
        table.addAgent(SimpleDefenseAgent(3))
        table.deal()
        winner,loser= table.gameStart(verbose=Verbose,UI=UI)
        if winner != None:
            winRecord[winner]+=1
        if loser != None:
            loseRecord[loser]+=1
        print ('**************************')
        if Verbose:
            if loser == 3:
                input()
        Round += 1.0
    print ('胡:', [winRecord[i]/Round for i in range(4)])
    print ('放槍:',[loseRecord[i]/Round for i in range(4)])
    for data in Table.loseReason[3]:
        print (data)
except KeyboardInterrupt:
    print ('胡:', [winRecord[i]/Round for i in range(4)])
    print ('放槍:',[loseRecord[i]/Round for i in range(4)])
    for data in Table.loseReason[3]:
        print (data)


