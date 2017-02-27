import pickle
import os
import numpy as np
import math
class DataSet:
    def __init__(self,batch_size,max_size,name = 'dataset'):
        assert batch_size < max_size, 'batch size cannot be greater than data size.'
        self.name = name
        self.batch_size = batch_size
        self.max_size = max_size
        self.setup()

    def setup(self):
        self.current_index = 0
        self.data = []
        self.num_batches = math.ceil(len(self.data) / self.batch_size)
        self.reset()

    def next_batch(self):
        if not self.has_next_batch():
            assert self.current_index == self.max_size
            return None
        else:
            from_ = self.current_index
            if from_ + self.batch_size <= self.max_size:
                to = from_ + self.batch_size
            else:
                to = self.max_size
            cur_idxs = self.indexes[from_:to]
            self.current_index = to
            data = [self.data[i] for i in cur_idxs]
            return zip(*data)
    
    def has_next_batch(self):
        return self.current_index < self.max_size
    
    def random_sample(self,size):
        indexes = range(len(self.data))
        np.random.shuffle(indexes)
        if size > len(self.data):
            cur_idxs = indexes
        else:
            cur_idxs = indexes[:size]

        data = [self.data[i] for i in cur_idxs]
        return zip(*data)
    
    def add(self,d):
        if len(self.data) > self.max_size:
            self.data.pop(0)
        
        self.data.append(d)
        self.num_batches = math.ceil(len(self.data) / self.batch_size)
    
    def reset(self):
        self.current_index = 0


