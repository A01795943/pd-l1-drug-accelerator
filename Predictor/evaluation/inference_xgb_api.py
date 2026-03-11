import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import sys
import os
import json
import joblib
import numpy as np
import torch
import contextlib
import io

# permitir importar desde models
sys.path.append(".")

from models.esm2_embedder import ESM2Embedder


# -----------------------------
# Validar argumento CLI
# -----------------------------
if len(sys.argv) != 2:
    print(json.dumps({"error": "Uso: python evaluation/inference_xgb_api.py <sequence>"}))
    sys.exit(1)

sequence = sys.argv[1]

# -----------------------------
# Detectar dispositivo
# -----------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# -----------------------------
# Ruta del modelo
# -----------------------------
model_path = "outputs/model_xgb.pkl"

if not os.path.exists(model_path):
    print(json.dumps({"error": "Modelo XGBoost no encontrado"}))
    sys.exit(1)

# -----------------------------
# Cargar modelo entrenado
# -----------------------------
model = joblib.load(model_path)

# -----------------------------
# Generar embedding ESM2
# -----------------------------
try:

    embedder = ESM2Embedder(device=device, batch_size=1)

    # silenciar prints internos del embedder
    with contextlib.redirect_stdout(io.StringIO()):
        embeddings = embedder.embed([sequence])

    X = np.array(embeddings)

except Exception as e:

    print(json.dumps({"error": f"Error generando embedding: {str(e)}"}))
    sys.exit(1)

# -----------------------------
# Predicción PTM / IPTM
# -----------------------------
try:

    preds = model.predict(X)

    ptm = float(preds[0][0])
    iptm = float(preds[0][1])

except Exception as e:

    print(json.dumps({"error": f"Error en predicción: {str(e)}"}))
    sys.exit(1)

# -----------------------------
# Salida JSON (para API)
# -----------------------------
result = {
    "sequence": sequence,
    "PTM_pred": ptm,
    "IPTM_pred": iptm
}

print(json.dumps(result))