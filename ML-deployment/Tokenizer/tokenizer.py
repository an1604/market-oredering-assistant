import re

import nltk
import torch
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

nltk.download('stopwords')
nltk.download('punkt')

"""
TODO:
In this case, I want to make a vocabulary for the products and tokenize there kind,
Also , I want to tokenize the query and classify the correct intention of the query.
So, I need to get 2 vocabularies at all: one for the products and one for the queries. 
and foreach that vocabulary I need to create a Vectorizer.
"""
stop_words = set(stopwords.words('english'))


def tokenize_sentence(text):
    tokens = word_tokenize(text.lower())
    stemming = [word for word in tokens if not word in stop_words]
    stemmer = PorterStemmer()
    return [stemmer.stem(word) for word in stemming]


def preprocess_text(text):
    # converts the text to lowercase, making all characters in the text lowercase.
    text = ' '.join(word.lower() for word in text.split(" "))
    # looks for specific punctuation marks like '.', ',', '!', and '?' in the text.
    text = re.sub(r"([.,!?])", r" \1 ", text)
    # Removes characters that are not letters (a-zA-Z) or the specified punctuation marks (.,!?).
    # It replaces them with a space.
    text = re.sub(r"[^a-zA-Z.,!?]+", r" ", text)
    return text


def predict_product_category(product_name, vectorizer, classifier, max_length):
    product_name = preprocess_text(product_name)
    vectorized_product = torch.Tensor(vectorizer.vectorize(product_name, vector_length=max_length))
    prediction = classifier(vectorized_product.unsqueeze(0), apply_softmax=True)

    probability_values, indices = prediction.max(dim=1)
    predicted_category = vectorizer.category_vocab.lookup_index(indices.item())

    return {
        'product_name': product_name,
        'predicted_category': predicted_category,
        'probability': probability_values.item()
    }


def predict_query_category(query, vectorizer, classifier, max_seq_length):
    query = preprocess_text(query)
    vectorized_query = torch.Tensor(vectorizer.vectorize(query, vector_length=max_seq_length))
    prediction = classifier(vectorized_query.unsqueeze(0), apply_softmax=True)

    probability_values, indices = prediction.max(dim=1)
    predicted_query = vectorizer.category_vocab.lookup_index(indices)
    return {
        'query': query,
        'predicted_category': predicted_query,
        'probability': probability_values.item()
    }
