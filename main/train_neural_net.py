# NOTE: Useful commands for Debian 10 PC:
# FOR CREATING CONTAINER AND ATTACHING SHELL: docker run --gpus all -it -v $PWD:/tmp/deepaero -w /tmp/deepaero  -p 7777:8080 --name peaceful_williamson tensorflow/tensorflow:latest-gpu-jupyter /bin/bash
# (Optional) ATTACH VS CODE SESSION: Click on green containers button -> Attach to running container. Open folder tmp/deepaero/
# FOR RUNNING TRAINING (INSIDE CONTAINER SHELL): python main/train_neural_net.py
# (If not attached to VS Code) FOR ATTACHING ANOTHER SHELL TO CONTAINER (INSIDE LOCAL SHELL): docker exec -it peaceful_williamson /bin/bash
# FOR RUNNING TENSORBOARD (INSIDE CONTAINER SHELL): tensorboard --logdir=/tmp/deepaero/logs/ --bind_all --port 8080
# FOR ACCESSING TENSORBOARD SESSION (LOCAL BROWSER): http://localhost:7777/

import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)) # Add parent directory to path
import numpy as np
from modules.generate_sample import generate_sample

def generator(batch_size=32):
	while True:  # Loop forever so the generator never terminates
		X = []
		y = []
		for _ in range(batch_size):
			X_element, y_element = generate_sample()
			X.append(X_element)
			y.append(y_element)
		X = np.array(X)
		y = np.array(y)
		yield X, y

train_generator = generator()
validation_generator = generator()

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten
from tensorflow.keras.callbacks import ModelCheckpoint, TensorBoard

filepath_mdl = 'model.h5'
checkpoint = ModelCheckpoint(filepath_mdl, monitor='val_loss', verbose=1, save_best_only=True)
tensorboard = TensorBoard(log_dir='./logs', batch_size=32, write_graph=True)
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
history_object = model.fit_generator(train_generator, validation_data=validation_generator, verbose=1, steps_per_epoch=50, epochs=1000, validation_steps=20, callbacks=callbacks_list)

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