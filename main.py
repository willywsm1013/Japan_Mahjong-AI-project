from Table import Table
from SimpleAgent import RandomAgent,OneStepAgent
from six.moves import cPickle    
table = Table(True)
record = [0]*4
repeat = 10000.0
data = []
pickle_name = './enemyAnalysis_oneStep_1000_1213'
for time in range(int(repeat)):
    table.newGame()
    for i in range(3):
        table.addAgent(OneStepAgent(i))
    table.addAgent(OneStepAgent(3))
    table.deal()
    winner = table.gameStart(True)
    if winner != None:
        record[winner]+=1
enemyData = table.getThrowsAndCombination()
print (enemyData)
print ('data lenth = ',len(enemyData))
f = open(pickle_name, 'wb')
cPickle.dump(enemyData, f, protocol=cPickle.HIGHEST_PROTOCOL)
f.close()
print ('save data to ',pickle_name)
print (record)
