#!/usr/bin/env python3
import sys
import os
import pandas as pd
import numpy as np
import joblib

# -------------------------------
# Archivos y directorios
# -------------------------------
model_file = "outputs/model_xgb.pkl"  # Modelo entrenado
output_dir = "outputs/inference"
os.makedirs(output_dir, exist_ok=True)

# -------------------------------
# Comprobar argumentos CLI
# -------------------------------
if len(sys.argv) != 2:
    print("Uso: python inference_xgb_batch.py <archivo_csv_secuencias>")
    sys.exit(1)

input_csv = sys.argv[1]

if not os.path.exists(input_csv):
    print(f"No se encontró el archivo {input_csv}")
    sys.exit(1)

print(f"Archivo de entrada: {input_csv}")

# -------------------------------
# Cargar modelo XGBoost
# -------------------------------
model = joblib.load(model_file)
print("Modelo XGBoost cargado ✅")

# -------------------------------
# Leer secuencias
# -------------------------------
df = pd.read_csv(input_csv)

if "seq" not in df.columns:
    print("El CSV debe tener una columna llamada 'seq'")
    sys.exit(1)

sequences = df["seq"].tolist()
print(f"Secuencias a procesar: {len(sequences)}")

# -------------------------------
# Función de embeddings
# -------------------------------
def embed_sequence(seq):
    """
    Genera embeddings de la secuencia usando la misma técnica que en entrenamiento.
    ⚠️ Reemplazar este ejemplo con tu función real de ESM2.
    """
    # Ejemplo dummy: reemplazar por embedding real
    embedding_dim = 1280  # cambiar al tamaño real de tu embedding
    return np.random.rand(embedding_dim)

# -------------------------------
# Generar embeddings para todas las secuencias
# -------------------------------
X = np.array([embed_sequence(seq) for seq in sequences])
print("Embeddings generados ✅")

# -------------------------------
# Predecir PTM e IPTM
# -------------------------------
preds = model.predict(X)

# Asegurar que preds tenga dos columnas
if preds.ndim == 1:
    preds = preds.reshape(-1, 2)

df["PTM_pred"] = preds[:, 0]
df["IPTM_pred"] = preds[:, 1]

# -------------------------------
# Guardar resultados
# -------------------------------
output_csv = os.path.join(output_dir, "predictions_batch.csv")
df.to_csv(output_csv, index=False)

print(f"Predicciones guardadas en: {output_csv}")