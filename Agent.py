class Agent :
    playerNumber = None
    action = None
    handcard = None
    def __init__(self,player_number,action):
        self.playerNumber = player_number
        self.action = action

    def goalTest(self):
        return true
    
    def initialHandCard(self,newHandcard):
        pass
