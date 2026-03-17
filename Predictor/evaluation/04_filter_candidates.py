import pandas as pd
import os

def filter_candidates():
    pred_file = "outputs/predictions_all_models.csv"
    
    if not os.path.exists(pred_file):
        print(f"❌ Error: No se encontró {pred_file}. Ejecuta primero la evaluación.")
        return

    df = pd.read_csv(pred_file)
    df.columns = df.columns.str.strip()

    # Usamos las columnas de promedio (Ensemble) que generamos en el notebook 03
    # Si no existen, las calculamos aquí rápidamente
    if "PTM_pred" not in df.columns:
        ptm_cols = [c for c in df.columns if "_PTM" in c]
        df["PTM_pred"] = df[ptm_cols].mean(axis=1)
    
    if "IPTM_pred" not in df.columns:
        iptm_cols = [c for c in df.columns if "_IPTM" in c]
        df["IPTM_pred"] = df[iptm_cols].mean(axis=1)

    # Thresholds científicos recomendados para AlphaFold2/Multimer
    threshold_ptm = 0.7
    threshold_iptm = 0.7

    print(f"\nFiltrando candidatos con PTM > {threshold_ptm} e IPTM > {threshold_iptm}...")

    candidates = df[(df["PTM_pred"] >= threshold_ptm) & (df["IPTM_pred"] >= threshold_iptm)].copy()
    discarded = df.drop(candidates.index).copy()

    # Guardar resultados
    os.makedirs("outputs", exist_ok=True)
    candidates.to_csv("outputs/alphafold_candidates.csv", index=False)
    discarded.to_csv("outputs/discarded.csv", index=False)

    print(f"✅ Total procesado: {len(df)}")
    print(f"🌟 Candidatos seleccionados: {len(candidates)}")
    print(f"🗑️ Descartados: {len(discarded)}")

if __name__ == "__main__":
    filter_candidates()