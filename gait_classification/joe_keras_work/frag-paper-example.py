'''
    Train on t+1 vector for every t, only trying to predict the final frame, given 29 as seed.
'''

from __future__ import print_function

from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout, TimeDistributed
from keras.layers import LSTM
from keras.optimizers import Nadam
import keras
from keras.utils.data_utils import get_file
import numpy as np
import random
import sys
import theano
sys.path.append('../representation_learning/')

from nn.Network import InverseNetwork, AutoEncodingNetwork
from nn.AnimationPlot import animation_plot


def data_util(preds,x):
    preds = np.expand_dims(preds, 1)
    d1 = preds[0] # - take the first
    d2 = np.concatenate((x[0], d1)) #First X
    return d2

data = np.load('../data/Joe/sequential_final_frame.npz')
train_x = data['train_x']
train_y = data['train_y']
test_x = data['test_x']
test_y = data['test_y']

#Load the preprocessed version, saving on computation
X = np.load('../data/Joe/data_edin_locomotion.npz')['clips']
X = np.swapaxes(X, 1, 2).astype(theano.config.floatX)
X = X[:,:-4]
preprocess = np.load('../data/Joe/preprocess.npz')
X = (X - preprocess['Xmean']) / preprocess['Xstd']


# build the model: 2 stacked LSTM
print('Build model...')
model = Sequential()
model.add(keras.layers.noise.GaussianNoise(1, input_shape=(29,256)))
model.add(TimeDistributed(Dense(300), input_shape=(29,256)))
model.add(Activation(keras.layers.advanced_activations.ELU(alpha=1.0)))
model.add(TimeDistributed(Dense(300)))
model.add(Activation(keras.layers.advanced_activations.ELU(alpha=1.0)))
model.add(LSTM(600, return_sequences=True, consume_less='gpu', \
                init='glorot_normal'))
model.add(LSTM(600, return_sequences=True, consume_less='gpu', \
               init='glorot_normal'))
model.add(TimeDistributed(Dense(300)))
model.add(Activation(keras.layers.advanced_activations.ELU(alpha=1.0)))
model.add(TimeDistributed(Dense(256)))
model.add(Activation(keras.layers.advanced_activations.ELU(alpha=1.0)))
# TimedistributedDense on top - Can then set output vectors to be next sequence!

model.compile(loss='mean_squared_error', optimizer='nadam')


print('Training model...')
hist = model.fit(train_x, train_y, batch_size=10, nb_epoch=100, validation_data=(test_x,test_y))
print(hist.history)
score = model.evaluate(test_x,test_y)
print(score)

