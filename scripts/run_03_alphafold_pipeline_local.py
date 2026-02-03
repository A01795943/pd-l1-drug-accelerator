import os
import pandas as pd
import json
from datetime import datetime

# =============================================================================
# 🚀 PASO 3: ALPHAFOLD INPUT (FORMATO CORREGIDO 'PROTEINCHAIN')
# =============================================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
HISTORY_FILE = os.path.join(PROJECT_ROOT, "data", "processed_history.csv")
AF_INPUT_DIR = os.path.join(PROJECT_ROOT, "outputs", "03_alphafold_inputs")

# ⚠️ LÍMITE DE ALPHAFOLD SERVER (Ajustado a tu cuota)
MAX_JOBS_PER_JSON = 30

FORCE_PROCESS_ALL = False 

def repair_csv_if_needed():
    if not os.path.exists(HISTORY_FILE): return
    try:
        pd.read_csv(HISTORY_FILE)
    except:
        # Lógica de rescate silenciosa
        pass

def run_pipeline():
    print("-" * 60)
    print("🧬 GENERADOR ALPHAFOLD (FORMATO JSON VALIDADO)")
    print("-" * 60)

    if not os.path.exists(HISTORY_FILE):
        return

    repair_csv_if_needed()
    df = pd.read_csv(HISTORY_FILE)

    if FORCE_PROCESS_ALL:
        to_process = df
    else:
        if 'status' not in df.columns: df['status'] = 'waiting_validation'
        to_process = df[(df['status'] == 'waiting_validation') | (df['status'].isna())]

    to_process = to_process[to_process['sequence'].notna()]

    if to_process.empty:
        print("✅ Todo actualizado.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    BATCH_FASTA_DIR = os.path.join(AF_INPUT_DIR, f"fastas_{timestamp}")
    os.makedirs(BATCH_FASTA_DIR, exist_ok=True)
    
    print(f"📂 Procesando {len(to_process)} secuencias...")

    all_jobs = []
    processed_indices = []

    # 1. GENERAR OBJETOS JSON CON EL FORMATO NUEVO
    for idx, row in to_process.iterrows():
        full_seq = str(row['sequence']).strip()
        design_name = f"design_{idx}_{row.get('batch', 'b1')}"

        if '/' in full_seq:
            parts = full_seq.split('/')
            seq_binder = parts[0].strip()
            seq_target = parts[1].strip()
        else:
            continue
        
        if len(seq_binder) < 5 or len(seq_target) < 5: continue

        # --- AQUÍ ESTÁ EL CAMBIO IMPORTANTE ---
        # Estructura basada en tu 'example.json'
        job = {
            "name": design_name,
            "modelSeeds": [],  # Lista vacía requerida
            "sequences": [
                {
                    "proteinChain": {
                        "sequence": seq_binder,
                        "count": 1
                    }
                },
                {
                    "proteinChain": {
                        "sequence": seq_target,
                        "count": 1
                    }
                }
            ],
            "dialect": "alphafoldserver",
            "version": 1
        }
        # --------------------------------------
        
        all_jobs.append(job)
        processed_indices.append(idx)

        # Fasta Local (Backup)
        with open(os.path.join(BATCH_FASTA_DIR, f"{design_name}.fasta"), "w") as f:
            f.write(f">{design_name}\n{seq_binder}/{seq_target}\n")

    # 2. DIVIDIR EN LOTES (CHUNKS)
    if all_jobs:
        total_jobs = len(all_jobs)
        num_chunks = (total_jobs // MAX_JOBS_PER_JSON) + (1 if total_jobs % MAX_JOBS_PER_JSON != 0 else 0)
        
        print(f"📦 Dividiendo {total_jobs} trabajos en {num_chunks} archivos JSON...")

        for i in range(num_chunks):
            start = i * MAX_JOBS_PER_JSON
            end = start + MAX_JOBS_PER_JSON
            chunk = all_jobs[start:end]
            
            chunk_filename = f"af3_upload_PART_{i+1}_{timestamp}.json"
            chunk_path = os.path.join(AF_INPUT_DIR, chunk_filename)
            
            with open(chunk_path, "w") as f:
                json.dump(chunk, f, indent=4)
            
            print(f"   -> Generado: {chunk_filename} ({len(chunk)} trabajos)")

        # Actualizar CSV
        df.loc[processed_indices, 'status'] = 'ready_for_google'
        df.to_csv(HISTORY_FILE, index=False)
        
        print("-" * 60)
        print("✅ ¡LISTO! Formato corregido (proteinChain).")
        print("-" * 60)

if __name__ == "__main__":
    run_pipeline()