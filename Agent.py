
#-*- coding: utf-8 -*-　

class Agent :
    playerNumber = None
    action = None
    handcard = None
    def __init__(self,player_number,action):
        self.playerNumber = player_number
        self.action = action
    
    def goalTest(self):
        return true
    
    ##########################################################
    ###   initial the first 13 hand card in the begining   ###
    ##########################################################
    def initialHandCard(self,newHandcard):
        pass



    ##############################################################################
    ###   get a new card, return state 'Throw' and a card which agent doesn't want   ###
    ##############################################################################
    def takeAction(self,newCard):
        return 'Throw',0



    ##############################################################################
    ###   check if agent can '吃' or '槓' by card and the agent who throw it   ###
    ###   should return state '吃', '槓', or None                              ###
    ############################################################################## 
    def check(self,agentNum,card): 
        return None
