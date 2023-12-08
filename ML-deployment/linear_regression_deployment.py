#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import joblib

df = pd.read_csv('data/Salary_Data.csv', header='infer')
df.sample(5)

X = df.iloc[:, :-1].values
y = df.iloc[:, -1].values

from sklearn.linear_model import LinearRegression

lr = LinearRegression().fit(X, y)

lr.score(X, y)

# Saving the model 
joblib.dump(lr, 'linear_regression_model.pkl')
