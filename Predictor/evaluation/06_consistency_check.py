import pandas as pd
import os

def check_consistency():
    files = {
        "Processed": "data/processed_dataset.csv",
        "Predictions": "outputs/predictions_all_models.csv",
        "Candidates": "outputs/alphafold_candidates.csv"
    }

    print("\n--- Running Consistency Check ---")
    
    dataframes = {}
    for name, path in files.items():
        if os.path.exists(path):
            dataframes[name] = pd.read_csv(path)
            print(f"✅ {name}: {len(dataframes[name])} filas.")
        else:
            print(f"❌ {name}: No encontrado en {path}")
            return

    # Validar que las secuencias de los candidatos existan en el dataset original
    preds_seqs = set(dataframes["Predictions"]['seq'])
    cand_seqs = set(dataframes["Candidates"]['seq'])
    
    missing = cand_seqs - preds_seqs
    if not missing:
        print("✅ Integridad de secuencias: OK (Todas existen en el dataset original)")
    else:
        print(f"⚠️ Alerta: {len(missing)} secuencias en candidatos no están en predicciones.")

    # Validar Thresholds
    cands = dataframes["Candidates"]
    failed_ptm = cands[cands["PTM_pred"] < 0.7]
    failed_iptm = cands[cands["IPTM_pred"] < 0.7]

    if len(failed_ptm) == 0 and len(failed_iptm) == 0:
        print("✅ Validación de Thresholds: OK (Todos cumplen > 0.7)")
    else:
        print(f"⚠️ Alerta: Hay {len(failed_ptm) + len(failed_iptm)} registros bajo el umbral.")

if __name__ == "__main__":
    check_consistency()