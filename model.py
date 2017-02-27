import tensorflow as tf
import numpy as np
from base_model import BaseModel
from data_util import DataSet
from tensorflow.contrib import layers
class FullyConnectedModel(BaseModel):
    '''
        This model uses fully connected network
    '''
    def build(self):
        params = self.params
        I = 34 ## size of input
        O = 1  ## size of output
        N = params.batch_size  ## size of batch
        N = None
        
        inputs = tf.placeholder('float32',shape = [N,I],name = 'x')  ## [num_batch, input_size]
        outputs = tf.placeholder('float32',shape = [N,O],name = 'y')   ## [num_batch, output_size]
        is_training = tf.placeholder(tf.bool)
        
        ###   three hidden layers
        l1 = layers.fully_connected(inputs = inputs,
                                    num_outputs = 1000,
                                    activation_fn = tf.nn.relu,
                                    trainable = True )
        #l1 = self.Dense(inputs,I,1000,activation = tf.nn.relu)
        l2 = self.Dense(l1,1000,500,activation = tf.nn.relu) 
        l3 = self.Dense(l2,500,250,activation = tf.nn.relu)
        qValues = self.Dense(l3,250,1,activation = None)
       
        with tf.name_scope('Loss'):
            ## mean square loss
            loss = tf.reduce_mean(tf.reduce_sum(tf.square(outputs-qValues),reduction_indices = [1]))
        
        ## trainning 
        def learning_rate_decay_fn(lr,global_step):
            return tf.train.exponential_decay(lr,
                                              global_step,
                                              decay_steps=3000,
                                              decay_rate = 0.5,
                                              staircase=True)
        OPTIMIZER_SUMMARIES = ['learning_rate',
                               'loss',
                               'gradients',
                               'gradient_norm']

        opt_op = tf.contrib.layers.optimize_loss(loss,
                                                self.global_step,
                                                learning_rate=params.learning_rate,
                                                optimizer=tf.train.AdamOptimizer,
                                                learning_rate_decay_fn=learning_rate_decay_fn,
                                                summaries=OPTIMIZER_SUMMARIES)
        ## placeholders
        self.x = inputs
        self.y = outputs
        self.is_training = is_training

        ## tensors
        self.loss = loss
        self.opt_op = opt_op
        self.qValues = qValues
    
    def get_feed_dict(self,batch,is_train):
        x = batch[0]    ## input
        r = batch[1]    ## reward
        ss = batch[2]   ## next input
        batch_size = len(x)
        y = []
        for i in range(batch_size):
            if ss[i] == None:
                y.append(r[i])
            else:
                qValues = self.test(ss[i])
                maxQ = max(qValues)
                y.append(r[i] + maxQ)
        
        return {
            self.x : x,
            self.y : y,
            self.is_training : is_train    
        }

