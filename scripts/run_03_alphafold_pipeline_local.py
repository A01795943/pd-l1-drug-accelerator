import os
import pandas as pd
import json
from datetime import datetime

# =============================================================================
# 🚀 ORQUESTADOR ALPHA FOLD 3 JSON (FORMATO OFICIAL) - PASO 3
# =============================================================================

# 1. Configuración de Rutas
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
HISTORY_FILE = os.path.join(PROJECT_ROOT, "data", "processed_history.csv")
AF_INPUT_DIR = os.path.join(PROJECT_ROOT, "outputs", "03_alphafold_inputs")

def prepare_validation_package():
    if not os.path.exists(HISTORY_FILE):
        print(f"❌ ERROR: No se encontró el historial en {HISTORY_FILE}")
        return

    os.makedirs(AF_INPUT_DIR, exist_ok=True)
    df = pd.read_csv(HISTORY_FILE)
    
    if 'status' not in df.columns:
        df['status'] = 'waiting_validation'

    # Filtramos las que necesitan validación
    to_process = df[df['status'] == 'waiting_validation']

    if to_process.empty:
        print("✅ No hay secuencias nuevas para procesar.")
        return

    print(f"🧬 Generando JSON oficial para {len(to_process)} diseños...")

    all_jobs_json = []

    for idx, row in to_process.iterrows():
        raw_seq = row['sequence']
        
        # Separación Binder/Target
        if '/' in raw_seq:
            binder_seq, target_seq = raw_seq.split('/')
        else:
            binder_seq = raw_seq
            target_seq = None

        job_id = f"design_{idx}_{row['batch']}"
        
        # --- ESTRUCTURA EXACTA REQUERIDA POR ALPHAFOLD 3 SERVER ---
        # Nota: Google usa camelCase (modelContents) y objetos anidados específicos
        model_entities = [
            {
                "protein": {
                    "sequence": binder_seq,
                    "label": "Binder_Designed"
                }
            }
        ]
        
        if target_seq:
            model_entities.append({
                "protein": {
                    "sequence": target_seq,
                    "label": "Target_Protein"
                }
            })

        job_structure = {
            "name": job_id,
            "modelContents": model_entities  # <--- Crucial: camelCase
        }
        
        all_jobs_json.append(job_structure)
        df.at[idx, 'status'] = 'ready_for_google'

    # Guardar el JSON
    json_output_path = os.path.join(AF_INPUT_DIR, "upload_to_google.json")
    with open(json_output_path, "w") as jf:
        json.dump(all_jobs_json, jf, indent=4)

    df.to_csv(HISTORY_FILE, index=False)
    
    print("-" * 60)
    print(f"✅ ¡JSON CORREGIDO GENERADO!")
    print(f"📂 Archivo: {json_output_path}")
    print(f"🚀 Súbelo ahora a https://alphafoldserver.com/")
    print("-" * 60)

if __name__ == "__main__":
    prepare_validation_package()