"""
Functions:
- load_fire_data_from_excel(path): Load and preprocess Excel fire dataset. Returns feature matrix X and target y.
- log_minmax_scale_fire_data(X_train, X_test, y_train, y_test): Applies log1p and MinMax scaling to fire data. Returns scaled versions and scalers.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

def load_fire_data_from_excel(path):
    df = pd.read_excel(path, engine="openpyxl", header=0).dropna()
    df.columns = [col.strip() for col in df.columns]
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]
    return X, y

def log_minmax_scale_fire_data(X_train, X_test, y_train, y_test):
    X_train_log, X_test_log = np.log1p(X_train), np.log1p(X_test)
    y_train_log, y_test_log = np.log1p(y_train), np.log1p(y_test)

    scaler_X, scaler_y = MinMaxScaler(), MinMaxScaler()
    X_train_scaled = scaler_X.fit_transform(X_train_log)
    X_test_scaled = scaler_X.transform(X_test_log)
    y_train_scaled = scaler_y.fit_transform(y_train_log.values.reshape(-1, 1))
    y_test_scaled = scaler_y.transform(y_test_log.values.reshape(-1, 1))

    return X_train_scaled, X_test_scaled, y_train_scaled, y_test_scaled, scaler_X, scaler_y