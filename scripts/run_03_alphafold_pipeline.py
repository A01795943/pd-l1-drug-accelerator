import os
import csv
import pandas as pd
from datetime import datetime

# =============================================================================
# 🚀 ORQUESTADOR ALPHA FOLD - AUTOMÁTICO & IDEMPOTENTE
# =============================================================================

# Detección de rutas
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# Rutas de datos
HISTORY_FILE = os.path.join(PROJECT_ROOT, "data", "processed_history.csv")
AF_INPUT_DIR = os.path.join(PROJECT_ROOT, "outputs", "03_alphafold_inputs")

# =============================================================================

def prepare_new_sequences():
    """
    Lee el historial y prepara archivos FASTA solo para las secuencias 
    que aún no han sido validadas por AlphaFold.
    """
    if not os.path.exists(HISTORY_FILE):
        print("⚠️ No hay historial de secuencias para procesar.")
        return

    os.makedirs(AF_INPUT_DIR, exist_ok=True)
    
    # Leer historial con Pandas para filtrar fácil
    df = pd.read_csv(HISTORY_FILE)
    
    # Filtro: Solo las que están en estado 'waiting_validation' o sin estado
    if 'status' not in df.columns:
        df['status'] = 'waiting_validation'
        
    to_process = df[df['status'] == 'waiting_validation']

    if to_process.empty:
        print("✅ No hay secuencias nuevas para validar en AlphaFold.")
        return

    print(f"🧬 Encontradas {len(to_process)} secuencias nuevas. Generando archivos FASTA...")

    for idx, row in to_process.iterrows():
        seq = row['sequence']
        batch = row['batch']
        
        # Nombre único para el archivo
        fasta_name = f"design_{batch}_{idx}.fasta"
        fasta_path = os.path.join(AF_INPUT_DIR, fasta_name)
        
        with open(fasta_path, "w") as f:
            f.write(f">design_{idx}\n{seq}\n")
            
        # Actualizar estado en el DataFrame local
        df.at[idx, 'status'] = 'fasta_ready'

    # Guardar el historial actualizado
    df.to_csv(HISTORY_FILE, index=False)
    print(f"📂 Archivos listos en: {AF_INPUT_DIR}")
    print("👉 El siguiente paso es subir estos FASTA a AlphaFold (Colab o Local).")

if __name__ == "__main__":
    prepare_new_sequences()