import pandas as pd

# Archivos
df_processed = pd.read_csv("data/processed_dataset.csv")
df_preds = pd.read_csv("outputs/predictions_all_models.csv")
df_candidates = pd.read_csv("outputs/alphafold_candidates.csv")

# 1️⃣ Revisar número de filas
print("Filas processed_dataset:", len(df_processed))
print("Filas predictions_all_models:", len(df_preds))
print("Filas alphafold_candidates:", len(df_candidates))

# 2️⃣ Revisar que las secuencias candidatas están en predictions_all_models
if 'seq' in df_candidates.columns and 'seq' in df_preds.columns:
    missing_seqs = set(df_candidates['seq']) - set(df_preds['seq'])
    if missing_seqs:
        print("⚠️ Secuencias candidatas NO están en predictions_all_models:", missing_seqs)
    else:
        print("✅ Todas las secuencias candidatas están en predictions_all_models")
else:
    print("⚠️ Falta columna 'seq' en predictions o candidatos")

# 3️⃣ Revisar thresholds
ptm_threshold = 0.7
iptm_threshold = 0.7
if 'PTM_pred' in df_candidates.columns and 'IPTM_pred' in df_candidates.columns:
    if (df_candidates['PTM_pred'] < ptm_threshold).any() or (df_candidates['IPTM_pred'] < iptm_threshold).any():
        print("⚠️ Hay candidatos que no cumplen thresholds")
    else:
        print("✅ Todos los candidatos cumplen thresholds")
else:
    print("⚠️ Falta columna 'PTM_pred' o 'IPTM_pred' en candidatos")