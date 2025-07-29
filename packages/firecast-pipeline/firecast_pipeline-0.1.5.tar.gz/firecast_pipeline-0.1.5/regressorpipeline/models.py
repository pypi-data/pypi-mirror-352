"""
Functions:
- train_ols_for_fire(X, y): Train Ordinary Least Squares regression for fire data.
- train_lasso_for_fire(X, y): Train Lasso regression on fire metrics.
- train_mlp_for_fire(X, y): Train MLP regressor for fire-related targets.
- train_xgboost_for_fire(X, y): Train XGBoost regressor for fire hazard prediction.
"""

from sklearn.linear_model import LinearRegression, Lasso
from sklearn.neural_network import MLPRegressor
import statsmodels.api as sm
import xgboost as xgb

def train_ols_for_fire(X, y):
    return sm.OLS(y, sm.add_constant(X)).fit()

def train_lasso_for_fire(X, y):
    model = Lasso(alpha=0.01).fit(X, y.ravel())
    return model

def train_mlp_for_fire(X, y):
    model = MLPRegressor(hidden_layer_sizes=(64, 64), max_iter=1000).fit(X, y.ravel())
    return model

def train_xgboost_for_fire(X, y):
    model = xgb.XGBRegressor(n_estimators=100).fit(X, y.ravel())
    return model