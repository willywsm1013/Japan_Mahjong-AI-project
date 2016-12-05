#-*- coding: utf-8 -*-　
import random
def RandomAction(handCards):
    return handCards.pop(random.randrange(len(handCards)))
