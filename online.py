#-*- coding: utf-8 -*-　
import BasicDefinition
import numpy as np 
from Agent import Agent
from BasicDefinition import CardIndex,WindIndex
import random
from SimpleAgent import *
from evalScore import evalScore 
while True:
    selfagent = OneStepAgent()
    agentnow = selfagent
    if agentnow