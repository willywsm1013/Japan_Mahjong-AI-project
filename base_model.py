import sys
import tensorflow as tf
import numpy as np
import json
import os
from tqdm import tqdm
class BaseModel(object):
    def __init__(self,params):
        ##  set parmas  ##
        self.params = params
        self.action = params.mode

        ##  dirs  ##
        self.save_dir = params.save_dir
        self.load_dir = params.load_dir
        self.summary_dir = os.path.join(self.save_dir,'RL_summary') 
        
        ##  model name  ##
        self.name = params.model_name
        
        ##  build model graph  ##
        self.graph = tf.Graph()
        self.sess = tf.Session(graph = self.graph)
        with self.graph.as_default():
            with tf.variable_scope(self.name):
                print ('Building ',self.name,'...')
                self.global_step = tf.Variable(0,name = 'global_step',trainable = False)
                self.build()
                self.merged = tf.summary.merge_all()
                self.init_op = tf.global_variables_initializer()

        ##  init saver  ##
        with self.graph.as_default():
            self.saver = tf.train.Saver()
        
        ##  init variables  ##
        if self.load_dir !=  None:
            self.load()
        else:
            if tf.gfile.Exists(self.summary_dir):
                tf.gfile.DeleteRecursively(self.summary_dir)
            print ('Init model...')
            self.sess.run(self.init_op)
        
        ##  summary writer  ##
        if self.action != 'test':
            self.summary_writer = tf.summary.FileWriter(logdir = self.summary_dir,graph = self.sess.graph)
    
    def __del__(self):
        if hasattr(self,'sess'):
            self.sess.close()

    def build(self):
        raise NotImplementedError()
    def get_feed_dict(self,batch,is_train):
        raise NotImplementedError()
        
    def train_batch(self,batch):
        feed_dict = self.get_feed_dict(batch, is_train=True)
        train_list = [self.merged, self.opt_op, sel.global_step]
        return self.sess.run(train_list, feed_dict=feed_dict)
    
    def test_batch(self,batch):
        feed_dict = {self.x:batch,self.is_training:False}
        #feed_dict = self.get_feed_dict(batch,is_train=False)
        test_list = [self.qValues]
        return self.sess.run(test_list, feed_dict=feed_dict)
    
    def train(self,train_data_set):
        params = self.params
        assert self.action != 'test'
        num_epochs = params.num_epochs
        
        batch = train_data_set.sample(params.batch_size)
        self.train_batch(batch) 
    
    def test(self,input_data):
        data_size = len(input_data)
        bs = self.params.batch_size
        tot_qValues = np.zeros((1,0),dtype = 'float32')
        index = 0
        while index != data_size:
            if index + bs < data_size :
                batch = input_data[index:index+bs]
                index += bs
            else :
                batch = input_data[index:data_size]
                index = data_size
            #print (len(batch)) 
            qValues = self.test_batch(batch)
            #print ('qq:',qValues)
            tot_qValues = np.append(tot_qValues,qValues)
        #print ('tot:',tot_qValues)
        #tot_qValues = sum(tot_qValues,[]) 
        return tot_qValues 
    
    def save(self,save_dir = None):
        assert self.action != 'test'
        import os
        if save_dir == None:
            print ('Saving model to dir %s' % self.save_dir)
            self.saver.save(self.sess, os.path.join(self.save_dir, 'run'), self.global_step)
        else:
            print ('Saving model to dir %s' % save_dir)
            self.saver.save(self.sess, os.path.join(save_dir, 'run'), self.global_step)

    def load(self,load_dir = None): 
        print("Loading model ...")
        if load_dir == None :
            checkpoint = tf.train.get_checkpoint_state(self.load_dir)
        else :
            checkpoint = tf.train.get_checkpoint_state(load_dir)
        
        if checkpoint is None:
            print("Error: No saved model found. Please train first.")
            sys.exit(0)
        self.saver.restore(self.sess, checkpoint.model_checkpoint_path)
    
    def Dense(self,inputs,in_size,out_size,activation=None):
        Weights = tf.Variable(tf.random_normal([in_size,out_size]))
        biases = tf.Variable(tf.random_normal([1,out_size]))
        
        Wx_plus_b = tf.matmul(inputs,Weights)+biases

        if activation == None:
            outputs = Wx_plus_b
        else:
            outputs = activation(Wx_plus_b)
        return outputs

