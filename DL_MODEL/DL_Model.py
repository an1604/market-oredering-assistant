import os

import numpy as np
import pickle
import keras
from tensorflow.keras.preprocessing.sequence import pad_sequences
import re


def load_DL_model():
    tokenizer_pickle_file = r'C:\Users\adina\PycharmProjects\pythonProject1\ML-deployment\tokenizer.pickle'
    model_json_file = r'C:\Users\adina\PycharmProjects\pythonProject1\ML-deployment\model.json'

    with open(tokenizer_pickle_file, 'rb') as tk:
        tokenizer = pickle.load(tk)

    json_file = open(model_json_file, 'r')
    loaded_model_json = json_file.read()
    json_file.close()

    lstm_model = keras.models.model_from_json(loaded_model_json)

    file_path = os.path.abspath(r'C:\Users\adina\PycharmProjects\pythonProject1\ML-deployment\model.h5')
    lstm_model.load_weights(file_path)

    return lstm_model, tokenizer


def sentiment_prediction(review):
    lstm_model, tokenizer = load_DL_model()

    test = tokenizer.texts_to_sequences([review.lower()])
    test = pad_sequences(test, maxlen=30, dtype='int32', value=0)

    sentiment = lstm_model.predict(test)[0]
    if np.argmax(sentiment) == 0:
        pred = 'Negative'
    elif np.argmax(sentiment) == 1:
        pred = 'Positive'
    return pred
