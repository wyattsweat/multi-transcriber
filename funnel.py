import librosa
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#%matplotlib inline
import os
from PIL import Image
import pathlib
import csv
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import keras
from keras import layers
from keras import layers
import keras
from keras.models import Sequential
import warnings
import pandas as pd
from pydub import AudioSegment
warnings.filterwarnings('ignore')


#partially taken and modified from https://www.kdnuggets.com/2020/02/audio-data-analysis-deep-learning-python-part-1.html

df = pd.read_csv('custom_trainset.csv')

#dft = pd.read_csv('custom_trainset.csv')
#dft2 = df.sample(n=20).reset_index()
#dft=dft.append(dft2)

print(df.head())

cmap = plt.get_cmap('inferno')
plt.figure(figsize=(8,8))
genres = 'blues classical country disco hiphop jazz metal pop reggae rock'.split()
words = '6491 6492 6493'.split()




header = 'filename chroma_stft rmse spectral_centroid spectral_bandwidth rolloff zero_crossing_rate label'
for i in range(1, len(df)+1):
    header += f' mfcc{i}'
header += ' label'
header = header.split()


file = open('dataset.csv', 'w', newline='')
with file:
    writer = csv.writer(file)
    writer.writerow(header)
genres = 'blues classical country disco hiphop jazz metal pop reggae rock'.split()
words = '6491 6492 6493'.split()
for s in range(0,len(df)):
    filename=df['path'][s]
    y, sr = librosa.load(df['path'][s], mono=True, duration=30)
    rmse = librosa.feature.rms(y=y)
    chroma_stft = librosa.feature.chroma_stft(y=y, sr=sr)
    spec_cent = librosa.feature.spectral_centroid(y=y, sr=sr)
    spec_bw = librosa.feature.spectral_bandwidth(y=y, sr=sr)
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
    zcr = librosa.feature.zero_crossing_rate(y)
    mfcc = librosa.feature.mfcc(y=y, sr=sr)
    to_append = f'{filename} {np.mean(chroma_stft)} {np.mean(rmse)} {np.mean(spec_cent)} {np.mean(spec_bw)} {np.mean(rolloff)} {np.mean(zcr)}'    
    for e in mfcc:
        to_append += f' {np.mean(e)}'
    to_append += f' {df["speaker"][s]}'
    file = open('dataset.csv', 'a', newline='')
    with file:
        writer = csv.writer(file)
        writer.writerow(to_append.split())
        #print(to_append.split())

data = pd.read_csv('dataset.csv')
data.head()# Dropping unneccesary columns
data = data.drop(['filename'],axis=1)#Encoding the Labels
#genre_list = df.iloc[:,-1]
genre_list = df['speaker']#.iloc[1,:]
print(genre_list)

encoder = LabelEncoder()
y = encoder.fit_transform(genre_list)#Scaling the Feature columns
scaler = StandardScaler()
X = scaler.fit_transform(np.array(data.iloc[:, :-1], dtype = float))#Dividing data into training and Testing set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = Sequential()
model.add(layers.Dense(512, activation='relu', input_shape=(X_train.shape[1],)))
model.add(layers.Dense(512, activation='relu'))
model.add(layers.Dense(256, activation='relu'))
model.add(layers.Dense(128, activation='relu'))
model.add(layers.Dense(64, activation='relu'))
model.add(layers.Dense(32, activation='softmax'))
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

diar = model.fit(X_train,
                    y_train,
                    epochs=100,
                    batch_size=128)

model.save('ann')

model2 = keras.models.load_model('ann')


#print(np.array(data.iloc[:, :-1])[0], dtype=float)
print(y_test)

file = open('dataset2.csv', 'w', newline='')
filename='6491\sunday1.wav'
print(filename)
y, sr = librosa.load(filename, mono=True, duration=30)
rmse = librosa.feature.rms(y=y)
chroma_stft = librosa.feature.chroma_stft(y=y, sr=sr)
spec_cent = librosa.feature.spectral_centroid(y=y, sr=sr)
spec_bw = librosa.feature.spectral_bandwidth(y=y, sr=sr)
rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
zcr = librosa.feature.zero_crossing_rate(y)
mfcc = librosa.feature.mfcc(y=y, sr=sr)
to_append = f'{filename} {np.mean(chroma_stft)} {np.mean(rmse)} {np.mean(spec_cent)} {np.mean(spec_bw)} {np.mean(rolloff)} {np.mean(zcr)}'    
for e in mfcc:
    to_append += f' {np.mean(e)}'
#to_append += f' {df["speaker"][s]}'
print(to_append)
with file:
    writer = csv.writer(file)
    writer.writerow(header)
file = open('dataset2.csv', 'a', newline='')
with file:
    writer = csv.writer(file)
    writer.writerow(to_append.split())


data2 = pd.read_csv('dataset2.csv')
data2.head()# Dropping unneccesary columns
data2 = data2.drop(['filename'],axis=1)#Encoding the Labels

print(data2)

question = scaler.fit_transform(np.array(data2.iloc[:, :-1], dtype = float))
#question = scaler.fit_transform(np.fromstring(to_append2, dtype=float, sep=' ').reshape(1, -1))

#predictions = model.predict(X_test[:3])
#print("predictions shape:", predictions.shape)


y_prob = model2.predict(question) 
y_classes = y_prob.argmax(axis=-1)
print(y_classes)