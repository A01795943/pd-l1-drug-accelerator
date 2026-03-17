import warnings
warnings.filterwarnings("ignore")

import sys
import os
import json
import joblib
import numpy as np
import torch
import contextlib
import io

# Configurar rutas para importar ESM2Embedder
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(base_path)

try:
    from models.esm2_embedder import ESM2Embedder
except ImportError:
    print(json.dumps({"error": "No se pudo importar ESM2Embedder. Revisa la estructura de carpetas."}))
    sys.exit(1)

def run_inference():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Uso: python evaluation/inference_xgb_api.py <sequence>"}))
        sys.exit(1)

    # Limpiar secuencia (quitar / si es un complejo)
    raw_sequence = sys.argv[1].strip()
    clean_sequence = raw_sequence.replace("/", "")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_path = os.path.join(base_path, "outputs/model_xgb.pkl")

    if not os.path.exists(model_path):
        print(json.dumps({"error": f"Modelo no encontrado en {model_path}"}))
        sys.exit(1)

    try:
        # 1. Cargar Modelo XGBoost
        model = joblib.load(model_path)
        
        # 2. Generar Embedding con ESM-2
        # Redirigimos logs de torch/transformers para que no ensucien el JSON de salida
        f = io.StringIO()
        with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
            embedder = ESM2Embedder(device=device, batch_size=1)
            embeddings = embedder.embed([clean_sequence])
            X = embeddings.numpy() # Esto tiene 480 columnas

        # 3. Ajuste de Dimensiones (480 -> 481)
        # El modelo fue entrenado con [embeddings + score]. 
        # Si falta el score, añadimos un valor neutral (0.0) para que XGBoost no de error.
        n_expected = model.n_features_in_
        if X.shape[1] < n_expected:
            padding = np.zeros((X.shape[0], n_expected - X.shape[1]))
            X = np.concatenate([X, padding], axis=1)

        # 4. Predicción
        preds = model.predict(X)
        
        # 5. Formatear Resultado
        result = {
            "status": "success",
            "model": "XGBoost",
            "input_len": len(clean_sequence),
            "PTM_pred": round(float(preds[0][0]), 4),
            "IPTM_pred": round(float(preds[0][1]), 4)
        }
        print(json.dumps(result))

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    run_inference()