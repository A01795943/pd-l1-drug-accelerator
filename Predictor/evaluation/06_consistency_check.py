# evaluation/06_consistency_check.py

import pandas as pd
import os

# -----------------------------
# Archivos
# -----------------------------

processed_file = "data/processed_dataset.csv"
pred_file = "outputs/predictions_all_models.csv"
candidates_file = "outputs/alphafold_candidates.csv"

# -----------------------------
# Verificar existencia
# -----------------------------

for f in [processed_file, pred_file, candidates_file]:
    if not os.path.exists(f):
        raise FileNotFoundError(f"No se encontró {f}")

# -----------------------------
# Cargar archivos
# -----------------------------

df_processed = pd.read_csv(processed_file)
df_preds = pd.read_csv(pred_file)
df_candidates = pd.read_csv(candidates_file)

# -----------------------------
# Revisar número de filas
# -----------------------------

print("\nFilas processed_dataset:", len(df_processed))
print("Filas predictions_all_models:", len(df_preds))
print("Filas alphafold_candidates:", len(df_candidates))

# -----------------------------
# Validar secuencias
# -----------------------------

if 'seq' in df_candidates.columns and 'seq' in df_preds.columns:

    missing = set(df_candidates['seq']) - set(df_preds['seq'])

    if missing:
        print("⚠️ Secuencias candidatas no encontradas en predictions:")
        print(missing)
    else:
        print("✅ Todas las secuencias candidatas están en predictions")

else:
    print("⚠️ Falta columna 'seq'")

# -----------------------------
# Validar thresholds
# -----------------------------

ptm_threshold = 0.7
iptm_threshold = 0.7

if 'PTM_pred' in df_candidates.columns and 'IPTM_pred' in df_candidates.columns:

    invalid = df_candidates[
        (df_candidates["PTM_pred"] < ptm_threshold) |
        (df_candidates["IPTM_pred"] < iptm_threshold)
    ]

    if len(invalid) > 0:
        print("⚠️ Hay candidatos que NO cumplen thresholds")
    else:
        print("✅ Todos los candidatos cumplen thresholds")

else:
    print("⚠️ Falta PTM_pred o IPTM_pred en candidatos")

print("\nConsistency check terminado")