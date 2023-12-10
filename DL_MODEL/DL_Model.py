import os

import numpy as np
import pickle

from tensorflow._api.v2.compat.v1 import keras
from tensorflow.keras.preprocessing.sequence import pad_sequences
import re


def load_DL_model():
    tokenizer_pickle_file = r'C:\Users\adina\PycharmProjects\pythonProject1\ML-deployment\tokenizer.pickle'
    model_json_file =  r'C:\Users\adina\PycharmProjects\pythonProject1\ML-deployment\model.json'

    with open(tokenizer_pickle_file, 'rb') as tk:
        tokenizer = pickle.load(tk)

    json_file = open(model_json_file, 'r')
    loaded_model_json = json_file.read()
    json_file.close()

    lstm_model = keras.models.model_from_json(loaded_model_json)

    file_path = os.path.abspath("model.h5")
    lstm_model.load_weights(file_path)

    return lstm_model, tokenizer


def sentiment_prediction(review):
    input_review = [review.lower()]
    input_review = [re.sub('[^a-zA-z0-9\s]', '', x) for x in input_review]

    lstm_model, tokenizer = load_DL_model()

    input_feature = tokenizer.texts_to_sequences(input_review)
    input_feature = pad_sequences(input_feature, 1473, padding='pre')

    sentiment = lstm_model.predict(input_feature)[0]

    if np.argmax(sentiment) == 0:
        pred = 'Negative'
    elif np.argmax(sentiment) == 1:
        pred = 'Positive'
    return pred
