
# 🔥 firecast_pipeline

This repository provides a unified training and prediction pipeline for **fire risk regression tasks** using the following models:

- **OLS** (Ordinary Least Squares)
- **Lasso**
- **MLP** (Multi-layer Perceptron)
- **CNN** (with Optuna hyperparameter tuning)
- **XGBoost**

The pipeline is designed for `.xlsx` Excel datasets with flexible feature columns.

👉 **The last column must always be the response (target) variable** (e.g., Time to Flashover).

---

## 📁 Expected Excel Format

- **File type:** `.xlsx`
- **Structure:**
  - ✅ First row = column headers
  - ✅ All columns except the **last** = input features
  - ✅ Last column = fire risk target (e.g., TTF)
  - ❌ Unnecessary columns must be **removed**, not just hidden

### ✅ Example

| Thermal Inertia | HRRPUA | Ignition Temp | Time to Flashover |
|-----------------|--------|----------------|--------------------|
| 136500          | 725    | 400            | 42.5               |
| ...             | ...    | ...            | ...                |

---

## 📦 Installation

Install all required dependencies:

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install pandas numpy scikit-learn statsmodels xgboost torch optuna openpyxl joblib plotly
```

---

## 🚀 Training

### Train a single model

```python
from regressorpipeline.train import train_fire_model

model, metrics = train_fire_model("cnn", "examples/example_data_train.xlsx", save=True)
print(metrics)
```

This returns the trained model and metrics (R², MAE, MSE), and optionally saves the model to `examples/`.

---

### Train a CNN Ensemble

You can train the same dataset multiple times to build a more stable ensemble:

```python
from regressorpipeline.train import train_multiple_cnn_for_fire

models, run_metrics, ensemble_metrics = train_multiple_cnn_for_fire(
    "examples/example_data_train.xlsx", n_runs=3
)
print(ensemble_metrics)
```

The ensemble is saved as `examples/cnn_ensemble.joblib`.

---

### 🔧 CLI Training (Optional)

```bash
# Train and save model
python -m regressorpipeline.train --model_name cnn --data_path examples/example_data_train.xlsx

# Train without saving
python -m regressorpipeline.train --model_name mlp --data_path examples/example_data_train.xlsx --no_save
```

---

## 🔍 Prediction

### Predict from a saved model

```python
from regressorpipeline.predict import load_model_bundle, predict_fire_risk

models, scaler_X, scaler_y = load_model_bundle("examples/best_cnn_model.joblib")
preds = predict_fire_risk(models[0], scaler_X, scaler_y, "examples/example_data_test.xlsx")
```

### Predict from an ensemble (average results)

```python
from regressorpipeline.predict import load_model_bundle, predict_fire_risk_from_models

models, scaler_X, scaler_y = load_model_bundle("examples/cnn_ensemble.joblib")
avg_preds = predict_fire_risk_from_models(models, scaler_X, scaler_y, "examples/example_data_test.xlsx")
```

### 🔧 CLI Prediction

```bash
python -m regressorpipeline.predict \
  --model_path examples/best_cnn_model.joblib \
  --predict_path examples/example_data_test.xlsx \
  --output_path examples/predictions.csv
```

---

## 📊 Visualization (CNN only)

Generate a 3D surface plot for CNN predictions over any two features:

```python
from regressorpipeline.visualize import plot_fire_risk_surface_matplotlib

plot_fire_risk_surface_matplotlib(
    model,
    X_scaled_df,
    scaler_X,
    scaler_y,
    "ThermalInertia",
    "FuelLoadDensity",
    "CNN Surface",
    save_path="examples/cnn_surface.html",
)
```

---

## 📂 Folder Structure

```text
firecast_pipeline/
│
├── regressorpipeline/
│   ├── train.py                # Training logic
│   ├── predict.py              # Prediction logic
│   ├── visualize.py            # 3D surface visualization
│   ├── cnn_module.py           # CNN model definition
│   ├── models.py               # Traditional model trainers
│   └── data_utils.py           # Data loaders and scalers
│
├── examples/
│   ├── example_data_train.xlsx
│   ├── example_data_test.xlsx
│   └── best_cnn_model.joblib
│
├── requirements.txt
└── README.md
```

---

## 📜 License

MIT License – use freely for research or fire safety AI applications. For commercial use, please contact the authors.
