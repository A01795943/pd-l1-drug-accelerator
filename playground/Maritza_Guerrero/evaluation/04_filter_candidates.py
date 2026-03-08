import pandas as pd

# Leer predicciones
df = pd.read_csv("outputs/predictions_all_models.csv")

# Thresholds
threshold_ptm = 0.7
threshold_iptm = 0.7

# Filtrar candidatos
candidates = df[
    (df["PTM_pred"] > threshold_ptm) &
    (df["IPTM_pred"] > threshold_iptm)
]

discarded = df.drop(candidates.index)

# Guardar
candidates.to_csv("outputs/alphafold_candidates.csv", index=False)
discarded.to_csv("outputs/discarded.csv", index=False)

print("Candidatos:", len(candidates))
print("Descartados:", len(discarded))