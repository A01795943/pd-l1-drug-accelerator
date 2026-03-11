# evaluation/08_plot_professional_candidates.py

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# -----------------------------
# Paths
# -----------------------------
input_file = "outputs/predictions_all_models.csv"  # toda la base
plots_dir = "outputs/plots"
os.makedirs(plots_dir, exist_ok=True)

# -----------------------------
# Cargar datos
# -----------------------------
df = pd.read_csv(input_file)
print("Dataset cargado:", df.shape)

# -----------------------------
# Configuración
# -----------------------------
threshold_ptm = 0.7
threshold_iptm = 0.7
top_n = 10  # marcar top N secuencias según PTM_pred + IPTM_pred

# Calcular score combinado simple para ranking
df["combined_score"] = df["PTM_pred"] + df["IPTM_pred"]
df_sorted = df.sort_values(by="combined_score", ascending=False)
top_candidates = df_sorted.head(top_n)

# -----------------------------
# Gráfica profesional
# -----------------------------
plt.figure(figsize=(10,8))

# 1️⃣ Gradiente de densidad
sns.kdeplot(
    x=df["PTM_pred"],
    y=df["IPTM_pred"],
    fill=True,
    cmap="Blues",
    thresh=0,
    levels=100,
    alpha=0.6
)

# 2️⃣ Todos los puntos
plt.scatter(df["PTM_pred"], df["IPTM_pred"], s=50, c='grey', alpha=0.4, label="Candidatos")

# 3️⃣ Resaltar zona óptima
plt.fill_betweenx(
    y=[threshold_iptm, 1.0],
    x1=threshold_ptm,
    x2=1.0,
    color='green',
    alpha=0.15,
    label="Región óptima (PTM>0.7, IPTM>0.7)"
)

# 4️⃣ Marcar top secuencias
plt.scatter(
    top_candidates["PTM_pred"],
    top_candidates["IPTM_pred"],
    s=100,
    c='red',
    edgecolors='black',
    label=f"Top {top_n} secuencias"
)

# Etiquetar top secuencias
for _, row in top_candidates.iterrows():
    plt.text(
        row["PTM_pred"]+0.005,
        row["IPTM_pred"]+0.005,
        row["seq"][:6] + "...",
        fontsize=8,
        weight='bold',
        color='darkred'
    )

# 5️⃣ Línea ideal
plt.plot([0,1],[0,1],'k--', label="Ideal PTM = IPTM")

# -----------------------------
# Etiquetas y estilo
# -----------------------------
plt.xlabel("PTM predicho")
plt.ylabel("IPTM predicho")
plt.title(f"Distribución de candidatos - Total: {len(df)}")
plt.xlim(0,1)
plt.ylim(0,1)
plt.legend()
plt.grid(True)
sns.despine()

# -----------------------------
# Guardar figura
# -----------------------------
save_path = os.path.join(plots_dir, "alphafold_candidates_professional.png")
plt.savefig(save_path, dpi=300)
plt.close()

print(f"Gráfico profesional guardado en: {save_path}")