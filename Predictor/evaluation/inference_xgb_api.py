import warnings
warnings.filterwarnings("ignore")
import sys, os, json, joblib, numpy as np, torch, contextlib, io

# Configurar rutas
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(base_path)
from models.esm2_embedder import ESM2Embedder

def run_inference(sequence, energy_score):
    clean_sequence = sequence.replace("/", "")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_path = os.path.join(base_path, "outputs/model_xgb.pkl")

    try:
        # 1. Cargar Modelo (Ahora de 481 columnas)
        model = joblib.load(model_path)
        
        # 2. Generar Embedding ESM-2 (480 columnas)
        with contextlib.redirect_stdout(io.StringIO()):
            embedder = ESM2Embedder(device=device, batch_size=1)
            embeddings = embedder.embed([clean_sequence])
            X_emb = embeddings.numpy()

        # 3. Concatenar el Score real (Columna 481)
        # Convertimos el score a float y lo unimos
        val_score = float(energy_score)
        X_final = np.hstack([X_emb, [[val_score]]])

        # 4. Predicción
        preds = model.predict(X_final)
        
        return {
            "status": "success",
            "model": "XGBoost_Hibrido",
            "input_len": len(clean_sequence),
            "energy_score": val_score,
            "PTM_pred": round(float(preds[0][0]), 4),
            "IPTM_pred": round(float(preds[0][1]), 4)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # Uso: python script.py "SEC" 1.903
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Faltan argumentos. Uso: <secuencia> <score>"}))
    else:
        print(json.dumps(run_inference(sys.argv[1], sys.argv[2])))