import argparse
import pandas as pd
import numpy as np
import joblib
import torch


def predict_fire_risk(model, scaler_X, scaler_y, input_path):
    """
    Predict fire risk from a single model and scaler set.

    Parameters
    ----------
    model : trained model (sklearn or torch)
    scaler_X : fitted sklearn scaler
    scaler_y : fitted sklearn scaler
    input_path : str
        Path to input Excel file

    Returns
    -------
    np.ndarray : Predicted values in original scale
    """
    df = pd.read_excel(input_path, engine="openpyxl")
    X = np.log1p(df.select_dtypes(include=[np.number]))
    X_scaled = scaler_X.transform(X)

    if isinstance(model, torch.nn.Module):
        model.eval()
        with torch.no_grad():
            preds = model(torch.tensor(X_scaled, dtype=torch.float32).unsqueeze(1)).numpy()
    else:
        preds = model.predict(X_scaled)

    preds = np.expm1(scaler_y.inverse_transform(preds.reshape(-1, 1))).ravel()
    return preds


def predict_fire_risk_from_models(models, scaler_X, scaler_y, input_path):
    """
    Predict using multiple models and average their results.

    Parameters
    ----------
    models : list
        List of trained models (torch or sklearn)
    scaler_X : fitted sklearn scaler
    scaler_y : fitted sklearn scaler
    input_path : str
        Path to input Excel file

    Returns
    -------
    np.ndarray : Averaged predictions
    """
    df = pd.read_excel(input_path, engine="openpyxl")
    X = np.log1p(df.select_dtypes(include=[np.number]))
    X_scaled = scaler_X.transform(X)

    preds_list = []

    for m in models:
        if isinstance(m, torch.nn.Module):
            m.eval()
            with torch.no_grad():
                pred = m(torch.tensor(X_scaled, dtype=torch.float32).unsqueeze(1)).numpy()
        else:
            pred = m.predict(X_scaled)
        preds_list.append(pred)

    avg_pred = np.mean(np.stack(preds_list, axis=0), axis=0)
    avg_pred = np.expm1(scaler_y.inverse_transform(avg_pred.reshape(-1, 1))).ravel()
    return avg_pred


def load_model_bundle(model_path):
    """Utility to load model and scalers from .joblib file."""
    bundle = joblib.load(model_path)
    models = bundle.get("models") or [bundle["model"]]
    scaler_X = bundle["scaler_X"]
    scaler_y = bundle["scaler_y"]
    return models, scaler_X, scaler_y


def main():
    parser = argparse.ArgumentParser(description="Run fire risk prediction using trained model.")
    parser.add_argument("--predict_path", required=True, help="Path to .xlsx file with test features")
    parser.add_argument("--model_path", required=True, help="Path to .joblib trained model file")
    parser.add_argument("--output_path", default=None, help="Optional: path to save predictions as CSV")
    args = parser.parse_args()

    models, scaler_X, scaler_y = load_model_bundle(args.model_path)

    if len(models) == 1:
        preds = predict_fire_risk(models[0], scaler_X, scaler_y, args.predict_path)
    else:
        preds = predict_fire_risk_from_models(models, scaler_X, scaler_y, args.predict_path)

    print("\n🔥 Fire Risk Predictions:")
    print(preds)

    if args.output_path:
        df_out = pd.DataFrame({"Predicted Fire Risk": preds})
        df_out.to_csv(args.output_path, index=False)
        print(f"\n✅ Predictions saved to {args.output_path}")


if __name__ == "__main__":
    main()
