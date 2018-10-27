# NOTE: For launching TensorBoard session execute the following command:
#     tensorboard --logdir=D:/Repositories/DeepSystemID/logs/

import numpy as np
from generate_sample import generate_sample

def generator(batch_size=32):
	while True:  # Loop forever so the generator never terminates
		X = []
		y = []
		for i in range(batch_size):
			X_element, y_element = generate_sample()
			X.append(X_element)
			y.append(y_element)
		X = np.array(X)
		y = np.array(y)
		yield X, y

train_generator = generator()
validation_generator = generator()

from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.callbacks import ModelCheckpoint, TensorBoard

filepath_mdl = 'model.h5'
checkpoint = ModelCheckpoint(filepath_mdl, monitor='val_loss', verbose=1, save_best_only=True)
tensorboard = TensorBoard(log_dir='./logs', batch_size=32, write_graph=True, update_freq='epoch')
callbacks_list = [checkpoint, tensorboard]

model = Sequential()

model.add(Dense(1600, activation='relu', input_shape=(1600,)))
model.add(Dropout(0.3))

model.add(Dense(500, activation='relu'))
model.add(Dropout(0.3))

model.add(Dense(100, activation='relu'))
model.add(Dropout(0.3))

model.add(Dense(50, activation='relu'))
model.add(Dropout(0.3))

model.add(Dense(26))

model.compile(loss='mse', optimizer='adam')
history_object = model.fit_generator(train_generator, validation_data=validation_generator, verbose=1, steps_per_epoch=50, epochs=40, validation_steps=20, callbacks=callbacks_list)

#model.save('model.h5')

from keras.models import Model
import matplotlib.pyplot as plt

### plot the training and validation loss for each epoch
plt.plot(history_object.history['loss'])
plt.plot(history_object.history['val_loss'])
plt.title('model mean squared error loss')
plt.ylabel('mean squared error loss')
plt.xlabel('epoch')
plt.legend(['training set', 'validation set'], loc='upper right')
plt.show()