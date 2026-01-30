import os
import csv
import pandas as pd
from datetime import datetime

# =============================================================================
# 🚀 ORQUESTADOR ALPHA FOLD - PASO 3
# =============================================================================

# 1. Detección automática de la raíz del proyecto
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# 2. Rutas de archivos (Sincronizadas con tu nuevo orden visual)
HISTORY_FILE = os.path.join(PROJECT_ROOT, "data", "processed_history.csv")
AF_INPUT_DIR = os.path.join(PROJECT_ROOT, "outputs", "03_alphafold_inputs")

# =============================================================================

def prepare_sequences_for_validation():
    """
    Lee el historial y genera archivos FASTA solo para las secuencias 
    que ProteinMPNN acaba de crear.
    """
    if not os.path.exists(HISTORY_FILE):
        print("⚠️ No se encontró el archivo de historial. ¿Corriste el paso 02?")
        return

    # Crear carpeta de salida si no existe
    os.makedirs(AF_INPUT_DIR, exist_ok=True)
    
    # Cargar historial
    df = pd.read_csv(HISTORY_FILE)
    
    # Si no existe la columna de estado, la creamos
    if 'status' not in df.columns:
        df['status'] = 'waiting_validation'

    # Filtramos solo las que necesitan validación
    to_process = df[df['status'] == 'waiting_validation']

    if to_process.empty:
        print("✅ Todas las secuencias ya tienen sus archivos FASTA listos.")
        return

    print(f"🧬 Procesando {len(to_process)} nuevas secuencias para AlphaFold...")

    for idx, row in to_process.iterrows():
        sequence = row['sequence']
        batch = row['batch']
        
        # Nombre del archivo basado en el batch y el índice
        file_name = f"target_{batch}_{idx}.fasta"
        file_path = os.path.join(AF_INPUT_DIR, file_name)
        
        # Escribir el formato FASTA
        with open(file_path, "w") as f:
            f.write(f">design_{idx}_batch_{batch}\n{sequence}\n")
            
        # Actualizar el estado en el DataFrame
        df.at[idx, 'status'] = 'fasta_ready'

    # Guardar los cambios en el historial
    df.to_csv(HISTORY_FILE, index=False)
    
    print(f"📂 ¡Listos! Los archivos están en: {AF_INPUT_DIR}")
    print("💡 Ahora puedes subir estos archivos a ColabFold o correr tu versión local.")

if __name__ == "__main__":
    prepare_sequences_for_validation()