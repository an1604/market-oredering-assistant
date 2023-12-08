import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

dataset_path = r'C:\Users\adina\PycharmProjects\pythonProject1\ML-deployment\data\Social_Network_Ads.csv'
df = pd.read_csv(dataset_path)
X = df.iloc[:, 1:-1].values
y = df.iloc[:, -1].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3,
                                                    random_state=0)

logreg = LogisticRegression(random_state=0).fit(X_train, y_train)
print(logreg.score(X_test, y_test))

predictions = logreg.predict(X_test)
print(classification_report(y_test, predictions, target_names=["Non Purchased", "Purchased"]))

import pickle

pickle_out = open("logreg.pkl", "wb")
pickle.dump(logreg, pickle_out)
pickle_out.close()

pickle_in = open("logreg.pkl","rb")
model = pickle.load(pickle_in)
y_pred = model.predict(X_test)[0]
print(y_pred)
