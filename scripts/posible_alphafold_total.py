import os
import pandas as pd
import json
from datetime import datetime

# =============================================================================
# 🚀 PASO 3: ALPHAFOLD INPUT (VERSIÓN ILIMITADA / LOCAL / PRO)
# =============================================================================
# Este script genera UN SOLO archivo JSON con TODOS los trabajos.
# Ideal para:
# 1. Correr AlphaFold 3 instalado localmente.
# 2. Servicios de pago sin cuota de 30 trabajos.
# 3. Uso con ColabFold masivo.

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
HISTORY_FILE = os.path.join(PROJECT_ROOT, "data", "processed_history.csv")
AF_INPUT_DIR = os.path.join(PROJECT_ROOT, "outputs", "03_alphafold_inputs")

FORCE_PROCESS_ALL = False # True = Regenerar archivos para TODO el historial

def repair_csv_if_needed():
    if not os.path.exists(HISTORY_FILE): return
    try:
        pd.read_csv(HISTORY_FILE)
    except:
        print("🔧 Reparando CSV...")
        with open(HISTORY_FILE, 'r') as f: lines = f.readlines()
        data = []
        for line in lines[1:]:
            parts = line.strip().split(',')
            if len(parts) >= 1:
                row = parts[:5]
                while len(row) < 5: row.append("waiting_validation")
                data.append([x.replace('"', '').strip() for x in row])
        df = pd.DataFrame(data, columns=["sequence", "date", "batch", "source_pdb", "status"])
        df.to_csv(HISTORY_FILE, index=False)

def run_pipeline():
    print("-" * 60)
    print("🧬 GENERADOR ALPHAFOLD (MODO MASIVO / ILIMITADO)")
    print("-" * 60)

    if not os.path.exists(HISTORY_FILE):
        print(f"❌ No existe el historial: {HISTORY_FILE}")
        return

    repair_csv_if_needed()
    df = pd.read_csv(HISTORY_FILE)

    if FORCE_PROCESS_ALL:
        print("⚠️  Modo FORCE_PROCESS_ALL activado.")
        to_process = df
    else:
        if 'status' not in df.columns: df['status'] = 'waiting_validation'
        to_process = df[(df['status'] == 'waiting_validation') | (df['status'].isna())]

    # Limpieza
    to_process = to_process[to_process['sequence'].notna()]

    if to_process.empty:
        print("✅ Todo actualizado. No hay diseños pendientes.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    BATCH_FASTA_DIR = os.path.join(AF_INPUT_DIR, f"fastas_FULL_{timestamp}")
    os.makedirs(BATCH_FASTA_DIR, exist_ok=True)
    
    print(f"📂 Procesando {len(to_process)} secuencias en UN solo lote...")

    all_jobs_json = []
    processed_indices = []

    for idx, row in to_process.iterrows():
        full_seq = str(row['sequence']).strip()
        design_name = f"design_{idx}_{row.get('batch', 'b1')}"

        # Lógica de lectura directa (confiamos en el CSV limpio del Paso 2)
        if '/' in full_seq:
            parts = full_seq.split('/')
            seq_binder = parts[0].strip()
            seq_target = parts[1].strip()
        else:
            print(f"⚠️  [SALTADO] Fila {idx}: Falta separador '/'.")
            continue
        
        if len(seq_binder) < 5 or len(seq_target) < 5: continue

        # -----------------------------------------------
        # 1. JSON (Estructura Correcta: Objetos Separados)
        # -----------------------------------------------
        job = {
            "name": design_name,
            "modelContents": {
                "protein": [
                    {"sequence": seq_binder, "count": 1},
                    {"sequence": seq_target, "count": 1}
                ]
            }
        }
        all_jobs_json.append(job)

        # -----------------------------------------------
        # 2. FASTA LOCAL
        # -----------------------------------------------
        with open(os.path.join(BATCH_FASTA_DIR, f"{design_name}.fasta"), "w") as f:
            f.write(f">{design_name}\n{seq_binder}/{seq_target}\n")

        processed_indices.append(idx)

    # 3. Guardar UN SOLO archivo JSON GIGANTE
    if all_jobs_json:
        # Nota el nombre "_FULL_" para distinguirlo
        json_path = os.path.join(AF_INPUT_DIR, f"af3_upload_FULL_{timestamp}.json")
        
        with open(json_path, "w") as f:
            json.dump(all_jobs_json, f, indent=4)

        # Actualizar CSV
        df.loc[processed_indices, 'status'] = 'ready_for_google'
        df.to_csv(HISTORY_FILE, index=False)

        print("-" * 60)
        print(f"✅ ¡ÉXITO MASIVO! {len(all_jobs_json)} trabajos generados.")
        print(f"📄 JSON Maestro: {json_path}")
        print(f"📂 Carpeta FASTAs: {BATCH_FASTA_DIR}")
        print("-" * 60)
    else:
        print("❌ No se generaron trabajos válidos.")

if __name__ == "__main__":
    run_pipeline()