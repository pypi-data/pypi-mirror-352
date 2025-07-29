import argparse
import pandas as pd
import numpy as np
import joblib
import torch
import plotly.graph_objects as go

def plot_fire_risk_surface_matplotlib(
    model, X_scaled_df, scaler_X, scaler_y, feat1_name, feat2_name, title, save_path="fire_risk_surface.html"
):
    # Get index of the selected features
    feat_names = X_scaled_df.columns
    idx1, idx2 = feat_names.get_loc(feat1_name), feat_names.get_loc(feat2_name)

    # Create 30x30 grid over the selected features
    f1_vals = np.linspace(X_scaled_df.iloc[:, idx1].min(), X_scaled_df.iloc[:, idx1].max(), 30)
    f2_vals = np.linspace(X_scaled_df.iloc[:, idx2].min(), X_scaled_df.iloc[:, idx2].max(), 30)
    F1, F2 = np.meshgrid(f1_vals, f2_vals)

    # Initialize full grid with mean values and overwrite the two feature axes
    X_grid_full_scaled = np.tile(X_scaled_df.mean().values, (F1.size, 1))
    X_grid_full_scaled[:, idx1] = F1.ravel()
    X_grid_full_scaled[:, idx2] = F2.ravel()

    # Predict using CNN
    with torch.no_grad():
        Y_pred = model(torch.tensor(X_grid_full_scaled, dtype=torch.float32).unsqueeze(1)).numpy()

    # Inverse transform the input grid
    X_grid_log = scaler_X.inverse_transform(X_grid_full_scaled)
    X_grid_original = np.expm1(X_grid_log)

    # Extract original feature values for plotting
    F1_original = X_grid_original[:, idx1].reshape(F1.shape)
    F2_original = X_grid_original[:, idx2].reshape(F2.shape)

    # Inverse transform predictions
    y_grid_pred_log = scaler_y.inverse_transform(Y_pred.reshape(-1, 1)).ravel()
    y_grid_pred_original = np.expm1(y_grid_pred_log).reshape(F1.shape)

    # Create 3D surface plot
    fig = go.Figure(data=[go.Surface(
        z=y_grid_pred_original,
        x=F1_original,
        y=F2_original,
        colorscale='Viridis'
    )])

    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title=f"{feat1_name} (Original)",
            yaxis_title=f"{feat2_name} (Original)",
            zaxis_title="Predicted Fire Risk (Original)"
        ),
        width=1000,
        height=800,
        margin=dict(l=0, r=0, b=0, t=50)
    )

    fig.write_html(save_path)
    print(f"✅ 3D surface plot saved to: {save_path}")


def main():
    parser = argparse.ArgumentParser(description="Visualize CNN prediction surface for fire risk.")
    parser.add_argument("--feat1", required=True, help="Name of the first feature (X-axis)")
    parser.add_argument("--feat2", required=True, help="Name of the second feature (Y-axis)")
    parser.add_argument("--model_path", required=True, help="Path to best_cnn_model.joblib")
    parser.add_argument("--save_path", default="fire_risk_surface.html", help="Path to save the interactive HTML plot")
    args = parser.parse_args()

    # Load model bundle
    model_bundle = joblib.load(args.model_path)
    model = model_bundle["model"]
    scaler_X = model_bundle["scaler_X"]
    scaler_y = model_bundle["scaler_y"]
    feature_names = model_bundle["feature_names"]

    # Load and preprocess training data
    df = pd.read_excel("examples/example_data_train.xlsx").dropna()
    df.columns = [c.strip() for c in df.columns]
    X = df[feature_names]

    X_log = np.log1p(X)
    X_scaled = scaler_X.transform(X_log)
    X_scaled_df = pd.DataFrame(X_scaled, columns=feature_names)

    # Plot
    plot_fire_risk_surface_matplotlib(
        model=model,
        X_scaled_df=X_scaled_df,
        scaler_X=scaler_X,
        scaler_y=scaler_y,
        feat1_name=args.feat1,
        feat2_name=args.feat2,
        title=f"Fire Risk Surface: {args.feat1} vs {args.feat2}",
        save_path=args.save_path
    )


if __name__ == "__main__":
    main()
