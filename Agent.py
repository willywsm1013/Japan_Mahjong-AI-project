
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



    #######################################################################
    ###   Get a new card                                                ###
    ###   case 1 : Throw                                                ###
    ###       return state 'Throw' and a card the agent doesn't want    ###
    ###   case 2 : Win                                                  ###
    ###       return state 'Win' and None                               ###
    #######################################################################
    def takeAction(self,newCard):
        assert newCard != None
        return 'Win',None



    #####################################################################################
    ###   check if agent can '吃' or '槓' by card and the agent who throw it          ###
    ###   if return state '吃' or '槓', should return cards that fit this situation   ###
    ###   if return state None, then return cards of None                             ###
    #####################################################################################
    def check(self,agentNum,card): 
        return None,None


    #############################################
    ###   update other player's information   ###
    ############################################# 
    def update(self,otherAgent,cards):
        pass
