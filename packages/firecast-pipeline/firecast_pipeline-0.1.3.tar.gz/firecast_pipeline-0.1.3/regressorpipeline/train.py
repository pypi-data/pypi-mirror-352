"""
Functions:
- train_fire_model(model_name, data_path, save=True): Entry point to train a model and optionally save it.
- train_optuna_cnn_for_fire(X_train, y_train, X_test, y_test): Train CNN with Optuna tuning for fire hazard regression.
- train_multiple_cnn_for_fire(data_path, n_runs=5, save_path=None): Train same dataset multiple times and average ensemble results.
"""

from .models import (
    train_ols_for_fire as train_ols,
    train_lasso_for_fire as train_lasso,
    train_mlp_for_fire as train_mlp,
    train_xgboost_for_fire as train_xgb
)

from .cnn_module import CNNModel
from .data_utils import (
    load_fire_data_from_excel as load_excel_data,
    log_minmax_scale_fire_data as log_scale_transform
)

from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import statsmodels.api as sm
import joblib
import torch
import torch.nn as nn
import torch.optim as optim
import optuna
import pandas as pd
import numpy as np
import os


def train_fire_model(model_name, data_path, save=True):
    X, y = load_excel_data(data_path)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    X_train_scaled, X_test_scaled, y_train_scaled, y_test_scaled, scaler_X, scaler_y = log_scale_transform(X_train, X_test, y_train, y_test)

    if model_name == "cnn":
        model, metrics = train_optuna_cnn_for_fire(X_train_scaled, y_train_scaled, X_test_scaled, y_test_scaled)
    else:
        if model_name == "ols":
            model = train_ols(X_train_scaled, y_train_scaled)
            X_test_eval = sm.add_constant(X_test_scaled, has_constant="add")
        elif model_name == "lasso":
            model = train_lasso(X_train_scaled, y_train_scaled)
            X_test_eval = X_test_scaled
        elif model_name == "mlp":
            model = train_mlp(X_train_scaled, y_train_scaled)
            X_test_eval = X_test_scaled
        elif model_name == "xgboost":
            model = train_xgb(X_train_scaled, y_train_scaled)
            X_test_eval = X_test_scaled
        else:
            raise ValueError("Unsupported model name")

        y_pred = model.predict(X_test_eval)
        metrics = {
            "R²": r2_score(y_test_scaled, y_pred),
            "MAE": mean_absolute_error(y_test_scaled, y_pred),
            "MSE": mean_squared_error(y_test_scaled, y_pred)
        }

    if save:
        os.makedirs("examples", exist_ok=True)
        joblib.dump({
            "model": model,
            "scaler_X": scaler_X,
            "scaler_y": scaler_y,
            "feature_names": X.columns.tolist()
        }, os.path.join("examples", f"best_{model_name}_model.joblib"))

    print(f"\n🔥 Model '{model_name}' Evaluation:")
    for k, v in metrics.items():
        print(f"{k}: {v:.4f}")

    return model, metrics


def train_optuna_cnn_for_fire(X_train, y_train, X_test, y_test):
    X_train_tensor = torch.tensor(X_train, dtype=torch.float32).unsqueeze(1)
    y_train_tensor = torch.tensor(y_train, dtype=torch.float32)
    X_test_tensor = torch.tensor(X_test, dtype=torch.float32).unsqueeze(1)
    y_test_tensor = torch.tensor(y_test, dtype=torch.float32)

    def objective(trial):
        model = CNNModel(
            trial.suggest_int("num_filters1", 8, 32),
            trial.suggest_int("num_filters2", 16, 64),
            trial.suggest_int("fc1_size", 32, 128)
        )
        lr = trial.suggest_float("lr", 1e-4, 1e-2, log=True)
        optimizer = optim.Adam(model.parameters(), lr=lr)
        criterion = nn.MSELoss()

        for _ in range(100):
            model.train()
            optimizer.zero_grad()
            loss = criterion(model(X_train_tensor), y_train_tensor)
            loss.backward()
            optimizer.step()

        model.eval()
        with torch.no_grad():
            pred = model(X_test_tensor).detach().numpy()
        return -r2_score(y_test_tensor.numpy(), pred)

    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=10)

    best_params = study.best_params
    best_model = CNNModel(best_params["num_filters1"], best_params["num_filters2"], best_params["fc1_size"])
    optimizer = optim.Adam(best_model.parameters(), lr=best_params["lr"])
    criterion = nn.MSELoss()

    for _ in range(100):
        best_model.train()
        optimizer.zero_grad()
        loss = criterion(best_model(X_train_tensor), y_train_tensor)
        loss.backward()
        optimizer.step()

    best_model.eval()
    with torch.no_grad():
        preds = best_model(X_test_tensor).detach().numpy()

    y_true = y_test_tensor.numpy()
    metrics = {
        "R²": r2_score(y_true, preds),
        "MAE": mean_absolute_error(y_true, preds),
        "MSE": mean_squared_error(y_true, preds)
    }

    return best_model, metrics


def train_multiple_cnn_for_fire(data_path, n_runs=5, save_path="examples/cnn_ensemble.joblib"):
    X, y = load_excel_data(data_path)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    X_tr_scaled, X_te_scaled, y_tr_scaled, y_te_scaled, scaler_X, scaler_y = log_scale_transform(
        X_train, X_test, y_train, y_test
    )

    models = []
    metrics_list = []
    preds_list = []

    for _ in range(n_runs):
        model, metrics = train_optuna_cnn_for_fire(
            X_tr_scaled, y_tr_scaled, X_te_scaled, y_te_scaled
        )
        models.append(model)
        metrics_list.append(metrics)

        model.eval()
        with torch.no_grad():
            preds = model(torch.tensor(X_te_scaled, dtype=torch.float32).unsqueeze(1)).numpy()
        preds_list.append(preds)

    ensemble_preds = np.mean(np.stack(preds_list, axis=0), axis=0)
    ensemble_metrics = {
        "R²": r2_score(y_te_scaled, ensemble_preds),
        "MAE": mean_absolute_error(y_te_scaled, ensemble_preds),
        "MSE": mean_squared_error(y_te_scaled, ensemble_preds),
    }

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        joblib.dump(
            {
                "models": models,
                "scaler_X": scaler_X,
                "scaler_y": scaler_y,
                "feature_names": X.columns.tolist(),
            },
            save_path,
        )

    return models, metrics_list, ensemble_metrics


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Train fire risk regression model.")
    parser.add_argument("--model_name", required=True, help="Model to train: ols, lasso, mlp, xgboost, cnn")
    parser.add_argument("--data_path", required=True, help="Path to training Excel file")
    parser.add_argument("--no_save", action="store_true", help="If set, do not save the trained model.")
    args = parser.parse_args()

    train_fire_model(args.model_name, args.data_path, save=not args.no_save)
