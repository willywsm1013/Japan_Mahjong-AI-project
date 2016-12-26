import operator
from functools import *

######################
###   計算組合數   ###
######################
def C(n,k):
    try :
        return  reduce(operator.mul, range(n - k + 1, n + 1)) /reduce(operator.mul, range(1, k +1)) 
    except TypeError:
        print ('(n,k) = ',(n,k))
