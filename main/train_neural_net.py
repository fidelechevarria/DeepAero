# NOTE: Commands for Debian 10 PC using conda env.
# python main/train_neural_net.py
# tensorboard --logdir=logs/

import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)) # Add parent directory to path
import numpy as np
from modules.generate_sample import generate_sample

def generator(batch_size=32):
	while True:  # Loop forever so the generator never terminates
		X = []
		y = []
		for idx in range(batch_size):
			X_element, y_element = generate_sample()
			X_element = np.expand_dims(X_element, axis=0)
			y_element = np.expand_dims(y_element, axis=0)
			if idx == 0:
				X = X_element
				y = y_element
			else:
				X = np.concatenate([X, X_element])
				y = np.concatenate([y, y_element])
		yield X, y

train_generator = generator()
validation_generator = generator()

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten, GRU, BatchNormalization
from tensorflow.keras.callbacks import ModelCheckpoint, TensorBoard

filepath_mdl = 'model.h5'
checkpoint = ModelCheckpoint(filepath_mdl, monitor='val_loss', verbose=1, save_best_only=True)
tensorboard = TensorBoard(log_dir='./logs', batch_size=32, write_graph=True)
callbacks_list = [checkpoint, tensorboard]

# create model
model = Sequential()

# model.add(Dense(1600, activation='relu', input_shape=(1600,)))
# model.add(Dropout(0.3))

# model.add(Dense(500, activation='relu'))
# model.add(Dropout(0.3))

# model.add(Dense(100, activation='relu'))
# model.add(Dropout(0.3))

# model.add(Dense(50, activation='relu'))
# model.add(Dropout(0.3))

# model.add(Dense(26))

model.add(GRU(256, return_sequences=True, input_shape=(16, 100)))
model.add(BatchNormalization())
model.add(Flatten())
model.add(Dense(26))

model.compile(loss='mse', optimizer='adam')
history_object = model.fit_generator(train_generator, validation_data=validation_generator, verbose=1, steps_per_epoch=500, epochs=100, validation_steps=20, callbacks=callbacks_list)

from tensorflow.keras.models import Model
import matplotlib.pyplot as plt

### plot the training and validation loss for each epoch
plt.plot(history_object.history['loss'])
plt.plot(history_object.history['val_loss'])
plt.title('model mean squared error loss')
plt.ylabel('mean squared error loss')
plt.xlabel('epoch')
plt.legend(['training set', 'validation set'], loc='upper right')
plt.show()