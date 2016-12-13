from Table import Table
from SimpleAgent import RandomAgent,OneStepAgent
    
table = Table(True)
record = [0]*4
repeat = 100.0
data = []
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
