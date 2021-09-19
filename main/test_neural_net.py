import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)) # Add parent directory to path
from modules.generate_sample import generate_sample
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM, BatchNormalization, Flatten
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


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

model.add(LSTM(1024, return_sequences=True, input_shape=(10, 100)))
model.add(BatchNormalization())
model.add(Flatten())
model.add(Dense(26))

# Compile model (required to make predictions)
model.compile(loss='mse', optimizer='adam')

print(model.summary())

# load weights
model.load_weights("model.h5")

# Generate sample
mode = 'sim'
if mode == 'real':
    data = pd.read_csv('data_real_processed.csv')
    X = np.expand_dims(np.transpose(data.loc[:, ['da', 'de', 'dr', 'dt', 'vx', 'vy', 'vz', 'p', 'q', 'r']].iloc[::12, :].values), axis=0)
elif mode == 'sim':
    X, y = generate_sample()
    X = np.expand_dims(X, axis=0)
    y = np.expand_dims(y, axis=0)

# estimate accuracy on whole dataset using loaded weights
if mode == 'sim':
    loss = model.evaluate(X, y)
prediction = model.predict(X)

# Visualization
if mode == 'real':
    data = {'Predict': prediction[0, :].tolist()}
elif mode == 'sim':
    data = {'Real': y[0, :].tolist(), 'Predict': prediction[0, :].tolist()}
df = pd.DataFrame(data)
if mode == 'sim':
    print('{}: {}'.format(model.metrics_names, loss))
print(df.round(5))

print(np.sum(np.abs(df['Real'].values - df['Predict'].values)))

