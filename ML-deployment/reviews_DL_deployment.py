import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from tensorflow import keras
import re
import pickle

dataset_path = r'C:\Users\adina\PycharmProjects\pythonProject1\ML-deployment\data\Restaurant_Reviews.tsv'

df = pd.read_csv(dataset_path, delimiter='\t', quoting=3)
df = df[['Review', 'Liked']]

df['Review'] = df['Review'].apply(lambda x: x.lower())
df['Review'] = df['Review'].apply(lambda x: re.sub('[^a-zA-Z0-9\s]', '', x))

max_features = 1000
tokenizer = keras.preprocessing.text.Tokenizer(num_words=max_features, split=' ')
tokenizer.fit_on_texts(df['Review'].values)
X = tokenizer.texts_to_sequences(df['Review'].values)
X = keras.preprocessing.sequence.pad_sequences(X)

embed_dim = 50
model = keras.models.Sequential()
model.add(keras.layers.Embedding(max_features, embed_dim, input_length=X.shape[1]))
model.add(keras.layers.LSTM(10))
model.add(keras.layers.Dense(2, activation='softmax'))
model.compile(loss='categorical_crossentropy',
              optimizer='adam', metrics=['accuracy'])
print(model.summary())

y = pd.get_dummies(df['Liked']).values
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=99)

model.fit(X_train, y_train, epochs=5, verbose=1)

test = ['Meal was pathetic']
test = tokenizer.texts_to_sequences(test)
test = keras.preprocessing.sequence.pad_sequences(test, maxlen=X.shape[1], dtype='int32', value=0)

liked = model.predict(test)[0]
if np.argmax(liked) == 0:
    print('Negative')
elif np.argmax(liked) == 1:
    print('Positive')

with open('tokenizer.pickle', 'wb') as tk:
    pickle.dump(tokenizer, tk, protocol=pickle.HIGHEST_PROTOCOL)

model_json = model.to_json()

with open("model.json", "w") as js:
    js.write(model_json)

model.save_weights("model.h5")


