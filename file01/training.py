# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 15:10:06 2017

@author: Administrator
"""
import os
import numpy as np
import tensorflow as tf
import input_data
import model#导入另外两个文件

#%%
N_CLASSES = 2
IMG_W = 208
IMG_H =208
BATCH_SIZE = 16
CAPACITY = 2000
MAX_STEP = 15000#with current parameter,it is suggested to use MAX_STEP>10k
learning_rate = 0.0001#with current parameters,it is suggested to use leaning rate<0.0001


#%%
def run_training():
    #with tf.Graph().as_default:
    train_dir = 'D:/anaconda/dailycode/catsVSdogs/catsvsdogs/data/train/'
    logs_train_dir='D:/anaconda/dailycode/catsVSdogs/catsvsdogs/logs/train/'
    
    train,train_label = input_data.get_files(train_dir)
    
    train_batch,train_label_batch = input_data.get_batch(train,
                                                         train_label,
                                                         IMG_W,
                                                         IMG_H,
                                                         BATCH_SIZE,
                                                         CAPACITY)
    train_logits = model.inference(train_batch,BATCH_SIZE,N_CLASSES)
    train_loss = model.losses(train_logits,train_label_batch)
    train_op = model.training(train_loss,learning_rate)
    train_acc = model.evaluation(train_logits,train_label_batch)
    
    summary_op = tf.summary.merge_all()#所有的summary弄到一块
    sess = tf.Session()
    train_writer = tf.summary.FileWriter(logs_train_dir,sess.graph)
    saver = tf.train.Saver
    
    sess.run(tf.global_variables_initializer())
    coord = tf.train.Coordinator()
    threads = tf.train.start_queue_runners(sess=sess,coord=coord)
    
    #开始训练
    try:
        for step in np.arange(MAX_STEP):#定义一个循环
            if coord.should_stop():
                break
            _,tra_loss,tra_acc = sess.run([train_op,train_loss,train_acc])
            
            if step%50==0:
                print('Step %d,train loss = %.2f,train accuracy = %.2f%%'%(step,tra_loss,tra_acc))
                summary_str = sess.run(summary_op)
                train_writer.add_summary(summary_str,step)
                
            if step %2000 == 0 or (step + 1)==MAX_STEP:
                checkpoint_path = os.path.join(logs_train_dir,'model.ckpt')
                saver().save(sess,checkpoint_path,global_step=step)
                
    except tf.errors.OutOfRangeError:
        print('Done training -- epoch limit reached')
    finally:
        coord.request_stop()
    coord.join(threads)
    sess.close()
                
#%%Evaluate one image
from PIL import Image
import matplotlib.pyplot as plt

def get_one_image(train):
    n = len(train)
    ind = np.random.randint(0,n)
    img_dir = train[ind]
    
    image = Image.open(img_dir)
    plt.imshow(image)
    image = np.array(image)
    
    return image

def evaluate_one_image():
    train_dir ='D:/anaconda/dailycode/catsVSdogs/catsvsdogs/data/train/'
    train,train_label =input_data.get_files(train_dir)
    image_array = get_one_image(train)
    
    with tf.Graph().as_default():
        BATCH_SIZE = 1
        N_CLASSES = 2#2分类
        
        image = tf.cast(image_array,tf.float32)
        image = tf.reshape(image,[1,208,208,3])#转化为4D
        logit = model.inference(image,BATCH_SIZE,N_CLASSES)
        logit = tf.nn.softmax(logit)
        
        x = tf.palceholder(tf.float32,shape = [208,208,3])
        
        logs_train_dir = 'D:/anaconda/dailycode/catsVSdogs/catsvsdogs/logs/train/'
        
        saver = tf.train.Saver()
        
        with tf.Session() as sess:
            print("Reading checkpoints...")
            ckpt = tf.train.get_checkpoint_state(logs_train_dir)
            if ckpt and ckpt.model_checkpoint_path:
                global_step = ckpt.model_checkpoint_path.split('/')[-1].split('.')[-1]
                saver.restore(sess,ckpt.model_checkpoint_path)
                print('Loading success,global_step is %s'% global_step)
                
            else:
                print("No checkpoint file found")
                
            prediction = sess.run(logit,feed_dict = {X:image_array})
            max_index = np.argmax(prediction)
            if max_index == 0:
                print('This is a cat with possiblity%.6f' %prediction[:,0])
            else:
                print('This is a dog with possiblity%.6f' %prediction[:,1])
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    