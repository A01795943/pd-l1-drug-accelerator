import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import sys

def plot_professional():
    # Rutas absolutas para tu entorno
    base_path = "/home/a01795976/accelerated-drug-design/Predictor"
    input_file = os.path.join(base_path, "outputs/predictions_all_models.csv")
    plots_dir = os.path.join(base_path, "outputs/plots")
    os.makedirs(plots_dir, exist_ok=True)

    if not os.path.exists(input_file):
        print(f"❌ Error: No se encuentra el archivo {input_file}")
        return

    df = pd.read_csv(input_file)
    
    # --- DETECCIÓN AUTOMÁTICA DE COLUMNAS ---
    # Prioridad: 1. Ensemble, 2. XGB, 3. Cualquier columna que termine en _PTM
    c_ptm, c_iptm = None, None
    
    if "Ensemble_PTM" in df.columns:
        c_ptm, c_iptm = "Ensemble_PTM", "Ensemble_IPTM"
    elif "xgb_PTM" in df.columns:
        c_ptm, c_iptm = "xgb_PTM", "xgb_IPTM"
    else:
        # Buscar la primera columna que parezca una predicción
        cols = [c for c in df.columns if c.endswith("_PTM") and "real" not in c]
        if cols:
            c_ptm = cols[0]
            c_iptm = c_ptm.replace("_PTM", "_IPTM")

    if not c_ptm or c_ptm not in df.columns:
        print(f"❌ Error: No se detectaron columnas de predicción. Columnas: {df.columns.tolist()}")
        return

    print(f"✅ Usando columnas para el gráfico: {c_ptm} y {c_iptm}")

    # Configuración de Selección
    threshold_ptm = 0.7
    threshold_iptm = 0.7
    top_n = 10 

    # Score combinado para ranking
    df["combined_score"] = df[c_ptm] + df[c_iptm]
    df_sorted = df.sort_values(by="combined_score", ascending=False)
    top_candidates = df_sorted.head(top_n)

    # Configuración estética
    plt.figure(figsize=(12, 10))
    sns.set_theme(style="whitegrid")

    # 1. Mapa de densidad (KDE)
    sns.kdeplot(
        x=df[c_ptm], y=df[c_iptm],
        fill=True, cmap="Blues", alpha=0.3, levels=15
    )

    # 2. Dataset Total
    plt.scatter(df[c_ptm], df[c_iptm], s=8, c='grey', alpha=0.15, label="Dataset Total")

    # 3. Zona de Interés
    plt.axvspan(threshold_ptm, 1.0, ymin=threshold_iptm, ymax=1.0, 
                color='green', alpha=0.08, label=f"Zona de Alta Confianza (>{threshold_ptm})")

    # 4. Top Candidatos
    plt.scatter(
        top_candidates[c_ptm], top_candidates[c_iptm],
        s=120, c='gold', edgecolors='black', marker='*', label=f"Top {top_n} Candidatos", zorder=5
    )

    # Etiquetas de texto para el Top 10
    for i, (idx, row) in enumerate(top_candidates.iterrows()):
        plt.text(
            row[c_ptm] + 0.008, row[c_iptm] + 0.008,
            f"ID_{i+1}: {row['seq'][:6]}...", 
            fontsize=10, weight='bold', color='darkred'
        )

    # 5. Línea de identidad
    plt.plot([0, 1], [0, 1], color='black', linestyle='--', alpha=0.3, label="PTM = IPTM")

    plt.xlabel(f"Predicted PTM ({c_ptm})", fontsize=13)
    plt.ylabel(f"Predicted IPTM ({c_iptm})", fontsize=13)
    plt.title(f"Mapeo Profesional de Candidatos AF2\n(Total: {len(df)} | Candidatos >0.7: {len(df[df[c_ptm] >= 0.7])})", fontsize=16)
    
    plt.xlim(0, 1.05)
    plt.ylim(0, 1.05)
    plt.legend(loc='upper left', frameon=True)
    sns.despine()
    
    save_path = os.path.join(plots_dir, "alphafold_candidates_professional.png")
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\n🚀 Gráfico profesional generado con éxito en:\n   {save_path}")

if __name__ == "__main__":
    plot_professional()