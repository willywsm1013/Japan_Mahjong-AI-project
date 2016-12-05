#-*- coding: utf-8 -*-　
from BasicDefinition import CardIndex
class Agent :
    playerNumber = None
    action = None
    handcard = None
    
    def __init__(self,player_number,action):
        self.playerNumber = player_number
        self.action = action
    
    def goalTest(self):
        s1 = []    #distinguish 4 color
        s2 = []
        s3 = []
        s4 = []
        self.handcard.sort()
        for card in self.handcard:
            if 1 <= card <= 9:
                s1.append(card)
            elif 11 <= card <=19:
                s2.append(card)
            elif 21 <= card <= 29:
                s3.append(card)
            else:
                s4.append(card)
        s = [s1,s2,s3]
        
        twoPair = 0
        while len(s4) != 0:
            count = s4.count(s4[0])
            if count == 3:
                s4 = s4[3:]
            elif count == 2:
                if twoPair == 0:
                    twoPair += 1
                    s4 = s4[2:]
                else:
                    return False
            else:
                return False
                
        for color in s:
            if len(color) != 0:
                if len(color) % 3 == 0:
                    while len(color) != 0:
                        first = color[0]
                        if color[1] == first:
                            if color[2] == first:
                                color = color[3:]
                            else:
                                return False
                        elif color[1] == first + 1:
                            if first + 2 in color:
                                color.remove(first + 2)
                                color = color[2:]
                            else:
                                return False
                        else:
                            return False
                elif len(color) % 3 == 2:
                    if twoPair != 0:
                        return False
                    else:
                        i = 0
                        correct1 = False
                        while i < len(color):
                            count = color.count(color[i])
                            if count > 1:
                                temp = color
                                del temp[i:i+2]
                                correct2 = True
                                while len(temp) != 0:
                                    first = temp[0]
                                    if temp[1] == first:
                                        if temp[2] == first:
                                            temp = temp[3:]
                                        else:
                                            correct2 = False
                                            break
                                    elif temp[1] == first + 1:
                                        if first + 2 in temp:
                                            temp.remove(first + 2)
                                            temp = temp[2:]
                                        else:
                                            correct2 = False
                                            break
                                    else:
                                        correct2 = False
                                        break
                                if correct2:
                                    correct1 = True
                                    break
                            i +=count
                        if not correct1:
                            return False
                else:
                    return False
        return True
    
    ##########################################################
    ###   initial the first 13 hand card in the begining   ###
    ##########################################################
    def initialHandCard(self,newHandcard):
        self.handcard = newHandcard



    #######################################################################
    ###   Get a new card                                                ###
    ###   case 1 : Throw                                                ###
    ###       return state 'Throw' and a card the agent doesn't want    ###
    ###   case 2 : 胡                                                   ###
    ###       return state '胡' and None                                ###
    #######################################################################
    def takeAction(self,newCard):
        if newCard != None :
            self.handcard.append(newCard)
        if self.goalTest():
            return '胡',None
        else:
            return 'Throw',self.action(self.handcard)####



    #####################################################################################
    ###   check if agent can '吃' or '槓' by card and the agent who throw it          ###
    ###   if return state '吃' or '槓', should return cards that fit this situation   ###
    ###   if return state None, then return cards of None                             ###
    ###   [[1,2,3],'吃',2]                                                            ###
    #####################################################################################
    def check(self,agentNum,card):
        self.handcard.append(card)
        if self.goalTest():
            return [self.handcard, '胡', card]
        self.handcard.remove(card)

        subtract = self.playerNumber - agentNum

        if subtract != 1 and subtract != -3 and self.handcard.count(card) == 3:
            return [[card,card,card,card], '槓', card]
        
        if subtract == 1 or subtract == -3:
            if 1 <= card <= 9 or 11 <= card <= 19 or 21 <= card <=29:
                if (card - 1 in self.handcard) and (card + 1 in self.handcard) and ((card - 1)%10 != 0) and ((card + 1)%10 != 0):
                    return [[card - 1,card,card + 1], '吃', card]
                elif (card - 2 in self.handcard) and (card - 1 in self.handcard) and ((card - 2)%10 != 0) and ((card - 1)%10 != 0):
                    return [[card -2,card -1,card], '吃', card]
                elif (card + 1 in self.handcard) and (card + 2 in self.handcard) and ((card + 1)%10 != 0) and ((card + 2)%10 != 0):
                    return [[card,card + 1,card +2], '吃', card]
                
        if self.handcard.count(card) == 2:
            return [[card,card,card], '碰', card]
        
        return [[], '過', card]


    #############################################
    ###   update other player's information   ###
    ############################################# 
    def update(self,otherAgent,cards):
        pass

    ###########################
    ###   print hand card   ###
    ###########################
    def printHandCard(self):
        sortedList = self.handcard[:]
        sortedList.sort()
        print ('Agent ',self.playerNumber,end =' :') 
        for card in sortedList :
            print (CardIndex[card],end=' ')
        print ()
