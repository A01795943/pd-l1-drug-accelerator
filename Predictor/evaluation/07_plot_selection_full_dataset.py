import pandas as pd
import matplotlib.pyplot as plt
import os

# ---------------------------------------
# Archivo con TODAS las predicciones
# ---------------------------------------

file_path = "outputs/predictions_all_models.csv"
plots_dir = "outputs/plots"

os.makedirs(plots_dir, exist_ok=True)

df = pd.read_csv(file_path)

print("Dataset completo:", df.shape)

# ---------------------------------------
# Thresholds AlphaFold
# ---------------------------------------

threshold_ptm = 0.7
threshold_iptm = 0.7

# ---------------------------------------
# Clasificación
# ---------------------------------------

selected = df[
    (df["PTM_pred"] > threshold_ptm) &
    (df["IPTM_pred"] > threshold_iptm)
]

discarded = df.drop(selected.index)

print("Candidatos:", len(selected))
print("Descartados:", len(discarded))

# ---------------------------------------
# Scatter plot
# ---------------------------------------

plt.figure(figsize=(8,7))

plt.scatter(
    discarded["PTM_pred"],
    discarded["IPTM_pred"],
    alpha=0.4,
    color="gray",
    label="Discarded"
)

plt.scatter(
    selected["PTM_pred"],
    selected["IPTM_pred"],
    alpha=0.9,
    color="red",
    label="AlphaFold candidates"
)

# líneas threshold
plt.axvline(threshold_ptm, linestyle="--", color="black")
plt.axhline(threshold_iptm, linestyle="--", color="black")

plt.xlabel("Predicted PTM")
plt.ylabel("Predicted IPTM")

plt.title("AlphaFold Candidate Selection")

plt.legend()
plt.grid(True)

save_path = f"{plots_dir}/alphafold_selection_full_dataset.png"

plt.savefig(save_path, dpi=300)
plt.close()

print("Gráfico guardado:", save_path)