#!/usr/bin/env python3
import sys
import os
import pandas as pd
import numpy as np
import joblib
import torch

# Importar embedder real
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.esm2_embedder import ESM2Embedder

def run_batch_inference():
    if len(sys.argv) != 2:
        print("Uso: python evaluation/inference_xgb_batch.py <archivo_csv_secuencias>")
        sys.exit(1)

    input_csv = sys.argv[1]
    model_file = "outputs/model_xgb.pkl"
    output_dir = "outputs/inference"
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(input_csv):
        print(f"❌ No se encontró el archivo {input_csv}")
        return

    # 1. Cargar datos y modelo
    print(f"📖 Cargando secuencias desde {input_csv}...")
    df = pd.read_csv(input_csv)
    if "seq" not in df.columns:
        print("❌ El CSV debe tener una columna 'seq'")
        return

    print("🧠 Cargando modelo XGBoost...")
    model = joblib.load(model_file)
    
    # 2. Generar Embeddings Reales
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🧬 Generando embeddings con ESM2 en {device}...")
    
    embedder = ESM2Embedder(model_name="esm2_t12_35M_UR50D", device=device, batch_size=16)
    
    # Procesar secuencias
    sequences = df["seq"].astype(str).tolist()
    embeddings = embedder.embed(sequences)
    X = embeddings.numpy()

    # 3. Predicción
    print("🚀 Ejecutando inferencia...")
    preds = model.predict(X)

    df["PTM_pred"] = preds[:, 0]
    df["IPTM_pred"] = preds[:, 1]

    # 4. Guardar resultados
    output_csv = os.path.join(output_dir, "predictions_batch.csv")
    df.to_csv(output_csv, index=False)
    
    # Filtrar automáticamente los mejores para ahorrar trabajo al usuario
    top_candidates = df[(df["PTM_pred"] >= 0.7) & (df["IPTM_pred"] >= 0.7)]
    top_csv = os.path.join(output_dir, "top_candidates_batch.csv")
    top_candidates.to_csv(top_csv, index=False)

    print(f"✅ Proceso terminado.")
    print(f"📊 Total procesado: {len(df)}")
    print(f"🌟 Candidatos detectados (>0.7): {len(top_candidates)}")
    print(f"💾 Resultados guardados en: {output_dir}")

if __name__ == "__main__":
    run_batch_inference()