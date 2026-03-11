# evaluation/04_filter_candidates.py

import pandas as pd
import os

# ------------------------------------------------
# Archivo de predicciones
# ------------------------------------------------

pred_file = "outputs/predictions_all_models.csv"

if not os.path.exists(pred_file):
    raise FileNotFoundError(f"No se encontró {pred_file}")

# ------------------------------------------------
# Leer predicciones
# ------------------------------------------------

df = pd.read_csv(pred_file)
df.columns = df.columns.str.strip()

print("Dataset cargado:", df.shape)

# ------------------------------------------------
# Verificar columnas necesarias
# ------------------------------------------------

required_cols = ["PTM_pred", "IPTM_pred"]

for col in required_cols:
    if col not in df.columns:
        raise ValueError(f"Falta la columna '{col}' en {pred_file}")

# ------------------------------------------------
# Thresholds
# ------------------------------------------------

threshold_ptm = 0.7
threshold_iptm = 0.7

print("\nThresholds utilizados:")
print("PTM >", threshold_ptm)
print("IPTM >", threshold_iptm)

# ------------------------------------------------
# Filtrar candidatos
# ------------------------------------------------

candidates = df[
    (df["PTM_pred"] > threshold_ptm) &
    (df["IPTM_pred"] > threshold_iptm)
].copy()

discarded = df.drop(candidates.index).copy()

# ------------------------------------------------
# Guardar resultados
# ------------------------------------------------

os.makedirs("outputs", exist_ok=True)

candidates_file = "outputs/alphafold_candidates.csv"
discarded_file = "outputs/discarded.csv"

candidates.to_csv(candidates_file, index=False)
discarded.to_csv(discarded_file, index=False)

# ------------------------------------------------
# Resumen
# ------------------------------------------------

total = len(df)
num_candidates = len(candidates)
num_discarded = len(discarded)

print("\nResumen filtrado")
print("Total secuencias:", total)
print("Candidatos:", num_candidates)
print("Descartados:", num_discarded)

print("\nArchivos generados:")
print(candidates_file)
print(discarded_file)