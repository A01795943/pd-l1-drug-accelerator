import os
import torch
import numpy as np
import pandas as pd
import joblib
import time
import sys

from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
from scipy.stats import spearmanr
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.neural_network import MLPRegressor
from xgboost import XGBRegressor

# Asegurar que podemos importar modelos personalizados
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.lightgbm_model import LightGBMModel

def run_training():
    print("\n" + "="*40)
    print("🚀 PIPELINE: MODEL TRAINING")
    print("="*40)

    # Crear directorios de salida
    os.makedirs("outputs/models", exist_ok=True)

    # --- 1. Cargar Datos ---
    print("\n[1/5] Cargando dataset y embeddings...")
    if not os.path.exists("data/processed_dataset.csv") or not os.path.exists("outputs/embeddings.pt"):
        print("❌ Error: Faltan archivos de entrada (CSV o Embeddings).")
        return

    df = pd.read_csv("data/processed_dataset.csv")
    embeddings = torch.load("outputs/embeddings.pt")
    
    # Extraer score de ProteinMPNN como feature adicional
    scores = df["score"].values.reshape(-1, 1)
    
    # Concatenar Embeddings (480/1280) + Score (1)
    X = np.concatenate([embeddings.numpy(), scores], axis=1)
    y = df[["PTM", "IPTM"]].values

    print(f"✅ Matriz de características: {X.shape}")
    print(f"✅ Matriz de objetivos: {y.shape}")

    # --- 2. Split Train/Test ---
    print("\n[2/5] Dividiendo dataset (80% Train, 20% Test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Guardar datos de test para evaluación posterior
    np.save("outputs/X_test.npy", X_test)
    np.save("outputs/y_test.npy", y_test)
    print("💾 Datos de test guardados en 'outputs/'")

    # --- 3. Definición de Modelos ---
    sklearn_models = {
        "ridge": MultiOutputRegressor(Ridge()),
        "rf": MultiOutputRegressor(RandomForestRegressor(n_estimators=100, max_depth=20, n_jobs=-1, random_state=42)),
        "xgb": MultiOutputRegressor(XGBRegressor(n_estimators=500, learning_rate=0.05, max_depth=7, tree_method="hist", n_jobs=-1, random_state=42)),
        "mlp_sklearn": MultiOutputRegressor(MLPRegressor(hidden_layer_sizes=(256, 128), max_iter=500, random_state=42))
    }

    results = []
    predictions = pd.DataFrame({
        "PTM_real": y_test[:, 0],
        "IPTM_real": y_test[:, 1]
    })

    # --- 4. Entrenamiento de Modelos Sklearn/XGB ---
    print("\n[3/5] Entrenando modelos principales...")
    for name, model in sklearn_models.items():
        print(f"  → Entrenando {name}...")
        start = time.time()
        model.fit(X_train, y_train)
        elapsed = time.time() - start
        
        # Guardar modelo
        joblib.dump(model, f"outputs/models/{name}.pkl")
        
        # Predecir y evaluar
        preds = model.predict(X_test)
        predictions[f"{name}_PTM"] = preds[:, 0]
        predictions[f"{name}_IPTM"] = preds[:, 1]

        for i, target in enumerate(["PTM", "IPTM"]):
            r2 = r2_score(y_test[:, i], preds[:, i])
            rmse = np.sqrt(mean_squared_error(y_test[:, i], preds[:, i]))
            sp = spearmanr(y_test[:, i], preds[:, i]).correlation
            results.append({"model": name, "target": target, "R2": r2, "RMSE": rmse, "Spearman": sp})

    # --- 5. LightGBM (Modelo Especializado) ---
    print("\n[4/5] Entrenando LightGBM...")
    lgbm = LightGBMModel()
    lgbm.fit(X_train, y_train)
    lgbm.save("outputs/models/lightgbm.pkl")
    
    lgbm_preds = lgbm.predict(X_test)
    predictions["lgb_PTM"] = lgbm_preds[:, 0]
    predictions["lgb_IPTM"] = lgbm_preds[:, 1]

    for i, target in enumerate(["PTM", "IPTM"]):
        r2 = r2_score(y_test[:, i], lgbm_preds[:, i])
        rmse = np.sqrt(mean_squared_error(y_test[:, i], lgbm_preds[:, i]))
        sp = spearmanr(y_test[:, i], lgbm_preds[:, i]).correlation
        results.append({"model": "lightgbm", "target": target, "R2": r2, "RMSE": rmse, "Spearman": sp})

    # --- Guardar Resultados Finales ---
    print("\n[5/5] Guardando métricas y predicciones...")
    predictions.to_csv("outputs/predictions_all_models.csv", index=False)
    metrics_df = pd.DataFrame(results)
    metrics_df.to_csv("outputs/model_metrics.csv", index=False)
    
    print("\n✅ ENTRENAMIENTO COMPLETADO EXITOSAMENTE")
    print(metrics_df.groupby('model')[['R2', 'Spearman']].mean())

if __name__ == "__main__":
    run_training()