import re
import string
from collections import Counter
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from nltk.stem import PorterStemmer, WordNetLemmatizer
from sklearn.model_selection import train_test_split


class Vocabulary(object):
    def __init__(self, token_to_idx=None):
        if token_to_idx is None:
            token_to_idx = {}

        self.token_to_idx = token_to_idx

        self.idx_to_token = {
            idx: token
            for idx, token in token_to_idx.items()
        }
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()

    def to_serializable(self):
        """ returns a dictionary that can be serialized """
        return {'token_to_idx': self.token_to_idx}

    @classmethod
    def from_serializable(cls, contents):
        """ instantiates the Vocabulary from a serialized dictionary """
        return cls(**contents)

    def add_token(self, token):
        token = self.stemmer.stem(token.lower())  # stemming
        token = self.lemmatizer.lemmatize(token)  # lemmatization
        if token in self.token_to_idx:
            index = self.token_to_idx[token]
        else:
            index = len(self.token_to_idx)
            self.token_to_idx[token] = index
            self.idx_to_token[index] = token

        return index

    def add_tokens(self, tokens):
        return [self.add_token(token) for token in tokens]

    def lookup_token(self, token):
        return self.token_to_idx[token]

    def lookup_index(self, index):
        if index not in self.idx_to_token:
            raise KeyError('The index (%d) is not in the vocabulary' % index)
        return self.idx_to_token[index]

    def __len__(self):
        return len(self.token_to_idx)

    def __str__(self):
        return "<Vocabulary(size=%d)>" % len(self)


class SequenceVocabulary(Vocabulary):
    def __init__(self, token_to_idx=None, unk_token='<UNK>', mask_token='<MASK>',
                 begin_seq_token='<BEGIN>', end_seq_token='<END>'):
        super(SequenceVocabulary, self).__init__(token_to_idx)
        self.unk_token = unk_token
        self.mask_token = mask_token
        self.begin_seq_token = begin_seq_token
        self.end_seq_token = end_seq_token

        self.mask_index = self.add_token(self.mask_token)
        self.unk_token = self.add_token(self.unk_token)
        self.begin_seq_index = self.add_token(self.begin_seq_token)
        self.end_seq_index = self.add_token(self.end_seq_token)

    def to_serializable(self):
        contents = super(SequenceVocabulary, self).to_serializable()
        contents.update({'unk_token': self.unk_token,
                         'mask_token': self.mask_token,
                         'begin_seq_token': self.begin_seq_token,
                         'end_seq_token': self.end_seq_token})
        return contents

    def lookup_token(self, token):
        if self.unk_token >= 0:
            return self.token_to_idx.get(token, self.unk_token)
        else:
            return self.token_to_idx[token]


class Vectorizer(object):
    def __init__(self, category_vocab, query_vocab):
        self.category_vocab = category_vocab
        self.query_vocab = query_vocab

    def vectorize(self, query, vector_length=-1):
        indices = [self.category_vocab.begin_seq_index]
        indices.extend(self.category_vocab.lookup_token(str(token))
                       for token in query.split(' '))
        indices.append(self.category_vocab.end_seq_index)

        if vector_length < 0:
            vector_length = len(indices)

        output = np.zeros(vector_length, dtype=np.int64)
        output[:len(indices)] = indices
        output[len(indices)] = self.category_vocab.mask_index
        return output

    @classmethod
    def from_dataframe(cls, df, cutoff=25):
        category_vocab = Vocabulary()
        for token in sorted(set(df['text'])):
            category_vocab.add_token(token)

        word_counter = Counter()
        for query in df['text']:
            for token in query.split(' '):
                if token not in string.punctuation:
                    word_counter[token] += 1

        query_vocab = SequenceVocabulary()
        for word, word_count in word_counter.items():
            if word_count > cutoff:
                query_vocab.add_token(word)

        return cls(category_vocab, query_vocab)


class QueryCategoryClassifier(nn.Module):
    def __init__(self, embedding_size, num_embeddings, num_channels,
                 hidden_dim, num_classes, dropout_p,
                 pretrained_embeddings=None, padding_idx=0):
        super(QueryCategoryClassifier, self).__init__()
        if pretrained_embeddings is None:
            self.emb = nn.Embedding(embedding_dim=embedding_size,
                                    num_embeddings=num_embeddings,
                                    padding_idx=padding_idx)
        else:
            pretrained_embeddings = torch.from_numpy(pretrained_embeddings).float()
            self.emb = nn.Embedding(num_embeddings=num_embeddings,
                                    embedding_dim=embedding_size,
                                    padding_idx=padding_idx,
                                    _weight=pretrained_embeddings)

        self.convent = nn.Sequential(
            nn.Conv1d(in_channels=embedding_size,
                      out_channels=num_channels,
                      kernel_size=3),
            nn.Conv1d(in_channels=num_channels,
                      out_channels=num_channels,
                      kernel_size=3),
            nn.ELU(),
            nn.Conv1d(in_channels=num_channels,
                      out_channels=num_channels, kernel_size=3,
                      stride=2),
            nn.ELU(),
            nn.Conv1d(in_channels=num_channels,
                      out_channels=num_channels,
                      kernel_size=3),
            nn.ELU()
        )

        self.dropout = dropout_p

        self.fc1 = nn.Linear(num_channels, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, num_classes)

    def forward(self, x_in, apply_softmax=False):
        x_emb = self.emb(x_in).permute(0, 2, 1)
        features = self.convent(x_emb)

        remaining_size = features.size(dim=2)
        features = F.avg_pool1d(features, remaining_size).squeeze(2)
        features = F.dropout(features, p=self._dropout_p)

        intermediate_vector = F.relu(F.dropout(self.fc1(features), p=self._dropout_p))
        prediction_vector = self.fc2(intermediate_vector)

        return prediction_vector


class TrainerClassifier(object):
    def __init__(self,
                 model: nn.Module,
                 optimizer: torch.optim.Optimizer,
                 loss: torch.nn.CrossEntropyLoss):
        self.model = model
        self.loss = loss
        setattr(self, 'optimizer', optimizer)

    def generate_batches(self,
                         X: torch.Tensor,
                         y: torch.Tensor,
                         batch_size: int = 32):
        N = X.shape[0]
        for ii in range(0, N, batch_size):
            X_batch, y_batch = X[ii:ii + batch_size], y[ii:ii + batch_size]
            yield X_batch, y_batch

    def fit(self, X_train: torch.Tensor,
            y_train: torch.Tensor,
            epochs: int = 100,
            batch_size: int = 32,
            eval_every: int = 10):
        for epoch in range(epochs):
            X_train, y_train = permute_data(X_train, y_train)
            batch_generator = self.generate_batches(X_train, y_train, batch_size)
            for ii, (X_batch, y_batch) in enumerate(batch_generator):
                self.optimizer.zero_grad()
                output = self.model(X_batch)
                loss = self.loss(output)
                loss.backward()
                self.optimizer.step()
            print('epoch: {}, loss: {}'.format(epoch, loss))

    def predict(self, X: torch):
        return self.model(X)


def permute_data(X: np.ndarray, y: np.ndarray):
    perm = np.random.permutation(X.shape[0])
    return X[perm], y[perm]


class QueryDataSet(Dataset):
    def __init__(self, df, vectorizer):
        self.vectorizer = vectorizer
        self.df = df

        measure_len = lambda contex: len(contex.split(' '))
        self._max_seq_length = max(map(measure_len, df.label)) + 2
        self.X = df.iloc[:, :-1].values
        self.y = df.iloc[:, -1]
        self.train_df, self.val_df, self.test_df = train_test_split(self.X, self.y, test_size=0.3,
                                                                    random_state=42)
        self.train_size = len(self.train_df)
        self.validation_size = len(self.val_df)
        self.test_size = len(self.test_df)

        self._lookup_dict = {'train': (self.train_df, self.train_size),
                             'val': (self.val_df, self.validation_size),
                             'test': (self.test_df, self.test_size)}

        class_counts = df.label.value_counts().to_dict()

        def sort_key(item):
            return self.vectorizer.category_vocab.lookup_token(item[0])

        sorted_counts = sorted(class_counts.items(), key=sort_key)
        frequencies = [count for _, count in sorted_counts]
        self.class_weights = 1.0 / torch.tensor(frequencies, dtype=torch.float32)

    @classmethod
    def load_dataset_and_make_vectorizer(cls, csv_file):
        df = pd.read_csv(csv_file)
        return cls(df, Vectorizer.from_dataframe(df))

    def get_vectorizer(self):
        return self.vectorizer

    def __len__(self):
        return self._target_size

    def get_num_batches(self, batch_size):
        return len(self) // batch_size


def generate_batches(dataset, batch_size, shuffle=True,
                     drop_last=True):
    dataloader = DataLoader(dataset=dataset, batch_size=batch_size,
                            shuffle=shuffle, drop_last=drop_last)

    for data_dict in dataloader:
        yield data_dict


if __name__ == "__main__":
    hidden_dim = 100
    num_channels = 100
    learning_rate = 0.001
    dropout_p = 0.1
    batch_size = 128
    num_epochs = 100
    embedding_size = 100
    hidden_dim = 10

    file_path = 'C:\\Users\\adina\\PycharmProjects\\pythonProject1\\ML-deployment\\data\\buy_remove_finish_data.csv'
    dataset = QueryDataSet.load_dataset_and_make_vectorizer(file_path)
    vectorizer = dataset.get_vectorizer()
    classifier = QueryCategoryClassifier(embedding_size=embedding_size,
                                         num_embeddings=len(vectorizer.category_vocab),
                                         num_channels=num_channels,
                                         hidden_dim=hidden_dim,
                                         num_classes=len(vectorizer.category_vocab),
                                         dropout_p=dropout_p,
                                         padding_idx=0)
    loss = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(classifier.parameters(), lr=learning_rate)
    trainer = TrainerClassifier(classifier, optimizer, loss)
    trainer.fit(X_train=dataset.X,
                y_train=dataset.y,
                batch_size=batch_size)
