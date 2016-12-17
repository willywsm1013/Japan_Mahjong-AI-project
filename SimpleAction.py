#-*- coding: utf-8 -*-　
import random
import sys
import tty
import os
import termios
#import curses
from BasicDefinition import CardIndex
def RandomAction(handCards,table=None):
    return handCards.pop(random.randrange(len(handCards)))




def getKey():
    def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ord(ch)
    state = None
    while True:
        ch = getch()
        if ch == 27:
            state = 27
        elif ch == 91 and state == 27:
            state = 2791
        elif ch == 68 and state == 2791:
            return 'Left'
        elif ch == 67 and state == 2791:
            return 'Right'
        elif ch == 13 and state == None:
            return 'Enter'
        elif ch == 3 and state == None:
            return 'Escape'
        else:
            state = None

def HumanAction_printTable(handCards,Table,pos):
    table = Table[:]
    space = int((len(table[-1][0])-55)/2)-1
    table.append([' '*(space+1+pos*3)+'*'])
    cards = handCards[:]
    cards.sort()
    r1 = [' '*space]
    r2 = [' '*space]
    for card in handCards :
        chinese = CardIndex[card]
        if len(chinese) == 2:
            r1.append(chinese[0])
            r2.append(chinese[1])
        else :
            r1.append('  ')
            r2.append(chinese[0])
    table.append(r1)
    table.append(r2)
    for row in table:
        print ('|'.join(map(str,row)))
    

def HumanAction_removeTable(table):
    for i  in table:
        print ("\b",end='')

def HumanAction(handCards,table):
    pos = len(handCards)-1
    key =None
    while(key != 'Enter'):
        if key == 'Left':
            if pos > 0 :
                pos-=1
            else :
                pos = len(handCards)-1 
        elif key == 'Right':
            if pos < len(handCards)-1:
                pos+=1
            else:
                pos = 0
        HumanAction_printTable(handCards,table,pos)
        key = getKey()
        if key == 'Escape':
            sys.exit()
        HumanAction_removeTable(table)
    return handCards.pop(pos)
