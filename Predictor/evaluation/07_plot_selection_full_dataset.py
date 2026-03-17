import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

def plot_selection():
    # Usar ruta absoluta para evitar problemas de ubicación
    base_path = "/home/a01795976/accelerated-drug-design/Predictor"
    file_path = os.path.join(base_path, "outputs/predictions_all_models.csv")
    
    if not os.path.exists(file_path):
        print(f"❌ Error: No se encuentra el archivo {file_path}")
        return

    df = pd.read_csv(file_path)
    
    # --- AJUSTE DE NOMBRES DE COLUMNAS ---
    # Cambiamos PTM_pred por Ensemble_PTM que es el nombre real en tu CSV
    col_ptm = "Ensemble_PTM"
    col_iptm = "Ensemble_IPTM"
    
    if col_ptm not in df.columns:
        print(f"⚠️ Columna {col_ptm} no encontrada. Columnas disponibles: {df.columns.tolist()}")
        # Intento de rescate: si no hay Ensemble, intentar con XGBoost
        if "xgb_PTM" in df.columns:
            col_ptm, col_iptm = "xgb_PTM", "xgb_IPTM"
            print("🔄 Usando predicciones de XGBoost en su lugar.")
        else:
            print("❌ No se encontraron columnas de predicción válidas.")
            return

    # Umbrales de selección (puedes ajustarlos aquí)
    t_ptm, t_iptm = 0.7, 0.7

    plt.figure(figsize=(10, 8))
    
    # 1. Fondo: Todos los puntos en gris con baja opacidad
    plt.scatter(df[col_ptm], df[col_iptm], c='lightgrey', alpha=0.3, s=5, label="Todas las Secuencias")
    
    # 2. Resaltar candidatos que pasan el filtro
    selected = df[(df[col_ptm] >= t_ptm) & (df[col_iptm] >= t_iptm)]
    
    if not selected.empty:
        plt.scatter(selected[col_ptm], selected[col_iptm], 
                    c='crimson', alpha=0.6, s=20, edgecolors='white', linewidth=0.5,
                    label=f"Candidatos AF2 (n={len(selected)})")
    
    # 3. Líneas de corte (Thresholds)
    plt.axvline(t_ptm, color='black', linestyle='--', lw=1.2, alpha=0.7)
    plt.axhline(t_iptm, color='black', linestyle='--', lw=1.2, alpha=0.7)

    # Anotaciones y estética
    plt.xlabel(f"Predicted PTM ({col_ptm.split('_')[0]})", fontsize=12)
    plt.ylabel(f"Predicted IPTM ({col_iptm.split('_')[0]})", fontsize=12)
    plt.title(f"Mapa de Selección de Candidatos\nBasado en Predicciones del Modelo", fontsize=15)
    plt.legend(loc='upper left', frameon=True, shadow=True)
    plt.grid(True, linestyle=':', alpha=0.4)

    # Guardar resultado
    plot_dir = os.path.join(base_path, "outputs/plots")
    os.makedirs(plot_dir, exist_ok=True)
    save_path = os.path.join(plot_dir, "selection_map.png")
    
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close() # Cerrar para liberar memoria
    
    print(f"📈 Gráfico de selección guardado en: {save_path}")
    print(f"🎯 Se han identificado {len(selected)} candidatos potenciales.")

if __name__ == "__main__":
    plot_selection()