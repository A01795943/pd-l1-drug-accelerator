# evaluation/05_evaluate_model.py

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score, mean_squared_error
import numpy as np
import os

# -----------------------------
# Archivos
# -----------------------------
real_file = "../data/processed_dataset.csv"
pred_file = "outputs/predictions_all_models.csv"

# -----------------------------
# Cargar datasets
# -----------------------------
df_real = pd.read_csv(real_file, sep=',')
df_real.columns = df_real.columns.str.strip()  # quitar espacios invisibles

df_pred = pd.read_csv(pred_file, sep=',')
df_pred.columns = df_pred.columns.str.strip()

# -----------------------------
# Verificar columnas
# -----------------------------
for c in ["PTM", "IPTM"]:
    if c not in df_real.columns:
        raise ValueError(f"Falta columna '{c}' en {real_file}")

# Modelos disponibles en predictions
models = ["ridge", "rf", "mlp", "xgb"]

# -----------------------------
# Evaluación por modelo
# -----------------------------
results = []

for model in models:
    ptm_col = f"{model}_PTM"
    iptm_col = f"{model}_IPTM"

    if ptm_col not in df_pred.columns or iptm_col not in df_pred.columns:
        print(f"⚠️ Columnas para {model} faltantes en {pred_file}, se omite.")
        continue

    y_true_ptm = df_real["PTM"][:len(df_pred)]
    y_true_iptm = df_real["IPTM"][:len(df_pred)]

    y_pred_ptm = df_pred[ptm_col]
    y_pred_iptm = df_pred[iptm_col]

    r2_ptm = r2_score(y_true_ptm, y_pred_ptm)
    r2_iptm = r2_score(y_true_iptm, y_pred_iptm)

    rmse_ptm = np.sqrt(mean_squared_error(y_true_ptm, y_pred_ptm))
    rmse_iptm = np.sqrt(mean_squared_error(y_true_iptm, y_pred_iptm))

    results.append({
        "model": model,
        "R2_PTM": r2_ptm,
        "R2_IPTM": r2_iptm,
        "RMSE_PTM": rmse_ptm,
        "RMSE_IPTM": rmse_iptm
    })

    print(f"\n=== Modelo: {model} ===")
    print(f"R2 PTM: {r2_ptm:.4f}, RMSE PTM: {rmse_ptm:.4f}")
    print(f"R2 IPTM: {r2_iptm:.4f}, RMSE IPTM: {rmse_iptm:.4f}")

    # -----------------------------
    # Graficos
    # -----------------------------
    plt.figure(figsize=(5,5))
    plt.scatter(y_true_ptm, y_pred_ptm, alpha=0.5)
    plt.plot([0,1],[0,1],'r--')
    plt.xlabel("PTM Real")
    plt.ylabel(f"PTM Predicción ({model})")
    plt.title(f"PTM: {model}")
    plt.grid(True)
    plt.show()

    plt.figure(figsize=(5,5))
    plt.scatter(y_true_iptm, y_pred_iptm, alpha=0.5)
    plt.plot([0,1],[0,1],'r--')
    plt.xlabel("IPTM Real")
    plt.ylabel(f"IPTM Predicción ({model})")
    plt.title(f"IPTM: {model}")
    plt.grid(True)
    plt.show()

# -----------------------------
# Guardar resultados
# -----------------------------
os.makedirs("../outputs", exist_ok=True)
df_results = pd.DataFrame(results)
df_results.to_csv("outputs/model_evaluation_metrics.csv", index=False)
print("\nMétricas guardadas en outputs/model_evaluation_metrics.csv")