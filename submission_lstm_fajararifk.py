# -*- coding: utf-8 -*-
"""submission_LSTM_FajarArifK.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1vfLziTw0QpcJKJSfEcncSngBhiAjN-40

Fajar Arif Kurniawan.
    https://data.world/data-society/global-climate-change-data
"""

# import data frame library
import pandas as pd
import json
import numpy as np

import warnings
warnings.filterwarnings('ignore')
# Visualization LIbrary
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
import scipy.stats as stats
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense, LSTM

data = pd.read_csv('GlobalLandTemperaturesByMajorCity.csv')
data.head()

data.drop(['City','Latitude','Longitude'], axis=1, inplace=True)
display(data)

"""Mengambil data dari tahun 28-07-1914 sampai 28-07-2013"""

data['dt'] = pd.to_datetime(data['dt'])
get_data = (data['dt'] >= '1914-07-28') & (data['dt'] <= '2013-07-28')
data = data.loc[get_data]
display(data)

data['Country'].value_counts()

"""Mengambil data miliki negara Indonesia"""

data = data.loc[data['Country'].isin(['China'])]
display(data)

data.drop(['Country'], axis=1, inplace=True)
data.reset_index(drop=True)

data.isnull().sum()

data.dropna(subset=['AverageTemperature'],inplace=True)
data.dropna(subset=['AverageTemperatureUncertainty'],inplace=True)
data.isnull().sum()

data_plot = data
data_plot[data_plot.columns.to_list()].plot(subplots=True, figsize=(16,8))
plt.show()

dates = data['dt'].values
tempe = data['AverageTemperature'].values

dates = np.array(dates)
temp = np.array(tempe)

plt.figure(figsize=(15,9))
plt.plot(dates, tempe)

plt.title('Average Temperature', fontsize = 20)
plt.ylabel('Temperature')
plt.xlabel('Datetime')

x_train, x_valid, y_train, y_valid = train_test_split(temp, dates, train_size=0.8, test_size = 0.2, shuffle = False )

print('Total Data Train : ',len(x_train))
print('Total Data Validation : ',len(x_valid))

def windowed_dataset(series, window_size, batch_size, shuffle_buffer):
    series = tf.expand_dims(series, axis=-1)
    ds = tf.data.Dataset.from_tensor_slices(series)
    ds = ds.window(window_size + 1, shift=1, drop_remainder = True)
    ds = ds.flat_map(lambda w: w.batch(window_size + 1))
    ds = ds.shuffle(shuffle_buffer)
    ds = ds.map(lambda w: (w[:-1], w[-1:]))
    return ds.batch(batch_size).prefetch(1)

tf.keras.backend.set_floatx('float64')

train_set = windowed_dataset(x_train, window_size=64, batch_size=200, shuffle_buffer=1000)
val_set = windowed_dataset(x_valid, window_size=64, batch_size=200, shuffle_buffer=1000)

model = Sequential([
    tf.keras.layers.LSTM(60, return_sequences=True),
    tf.keras.layers.LSTM(60),
    tf.keras.layers.Dense(30, activation="relu"),
    tf.keras.layers.Dense(10, activation="relu"),
    tf.keras.layers.Dense(1),
])

Mae = (data['AverageTemperature'].max() - data['AverageTemperature'].min()) * 10/100
print(Mae)

class myCallback(tf.keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs={}):
        if(logs.get('mae')<5.8 and logs.get('val_mae')<5.8):
            print("\nMAE dari model < 10% skala data")
            self.model.stop_training = True
callbacks = myCallback()

optimizer = tf.keras.optimizers.SGD(lr=1.0000e-04, momentum=0.9)

model.compile(loss=tf.keras.losses.Huber(),
              optimizer=optimizer,
              metrics=["mae"])

history = model.fit(train_set, epochs=100, validation_data = val_set, callbacks=[callbacks])

plt.plot(history.history['mae'])
plt.plot(history.history['val_mae'])
plt.title('Akurasi Model')
plt.ylabel('Mae')
plt.xlabel('epoch')
plt.legend(['Train', 'Val'], loc='upper left')
plt.show()

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Loss Model')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['Train', 'Val'], loc='upper left')
plt.show()