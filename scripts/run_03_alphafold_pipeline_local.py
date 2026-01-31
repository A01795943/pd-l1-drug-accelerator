import os
import pandas as pd
import json
import csv
from datetime import datetime

# =============================================================================
# 🚀 PASO 3: GENERADOR ALPHAFOLD (JSON + FASTA CON FORMATO COMPLEJO)
# =============================================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
HISTORY_FILE = os.path.join(PROJECT_ROOT, "data", "processed_history.csv")
AF_INPUT_DIR = os.path.join(PROJECT_ROOT, "outputs", "03_alphafold_inputs")

# Secuencia del Target (PD-L1 Humano)
# Esta secuencia se pegará después de la barra '/' en los FASTAs
PDL1_SEQUENCE = "MRIFAVFIFMTYWHLLNAFTVTVPKDLYVVEYGSNMTIECKFPVEKQLDLAALIVYWEMEDKNIIQFVHGEEDLKVQHSSYRQRARLLKDQLSLGNAALQITDVKLQDAGVYRCMISYGGADYKRITVKVNAPYNKINQRILVVDPVTSEHELTCQAEGYPKAEVIWTSSDHQVLSGKTTTTNSKREEKLFNVTSTLRINTTTNEIFYCTFRRLDPEENHTAELVIPELPLAHPPNER"

def repair_csv_if_needed():
    """Arregla el CSV si tiene columnas extra o corruptas."""
    try:
        pd.read_csv(HISTORY_FILE)
        return
    except Exception:
        print(f"🔧 Detectando CSV corrupto... Reparando...")
    
    recovered_data = []
    header = ["sequence", "date", "batch", "source_pdb", "status"]
    
    if not os.path.exists(HISTORY_FILE): return

    with open(HISTORY_FILE, 'r') as f:
        lines = f.readlines()

    # Empezamos desde la línea 1 para saltar el header viejo
    for line in lines[1:]:
        parts = line.strip().split(',')
        if len(parts) >= 4:
            clean_row = parts[:4]
            # Si falta status o está sucio, lo arreglamos
            if len(parts) == 4:
                clean_row.append("waiting_validation")
            else:
                clean_row.append(parts[4])
            
            clean_row = [x.replace('"', '').replace("'", "") for x in clean_row]
            recovered_data.append(clean_row)
    
    df_clean = pd.DataFrame(recovered_data, columns=header)
    df_clean.to_csv(HISTORY_FILE, index=False)
    print("✅ CSV estandarizado correctamente.")

def prepare_package():
    if not os.path.exists(HISTORY_FILE):
        print(f"❌ No existe: {HISTORY_FILE}")
        return

    repair_csv_if_needed()
    
    try:
        df = pd.read_csv(HISTORY_FILE)
    except Exception as e:
        print(f"❌ Error fatal leyendo CSV: {e}")
        return

    if 'status' not in df.columns:
        df['status'] = 'waiting_validation'

    # Filtrar solo lo nuevo
    to_process = df[(df['status'] == 'waiting_validation') | (df['status'].isna())]

    if to_process.empty:
        print("✅ No hay diseños nuevos para procesar.")
        return

    # Crear carpetas organizadas por fecha
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    BATCH_FASTA_DIR = os.path.join(AF_INPUT_DIR, f"fastas_{timestamp}")
    os.makedirs(BATCH_FASTA_DIR, exist_ok=True)
    
    print(f"🧬 Procesando {len(to_process)} diseños...")

    all_jobs_json = []

    for idx, row in to_process.iterrows():
        binder_seq = str(row['sequence']).strip()
        if not binder_seq or len(binder_seq) < 5: continue

        design_name = f"design_{idx}_{row.get('batch', 'b1')}"
        
        # 1. GENERAR JSON (Estructura oficial de Google - Objetos separados)
        job_structure = {
            "name": design_name,
            "modelContents": [
                {
                    "protein": {
                        "sequence": binder_seq,
                        "label": "Binder_Designed"
                    }
                },
                {
                    "protein": {
                        "sequence": PDL1_SEQUENCE,
                        "label": "Target_PDL1"
                    }
                }
            ]
        }
        all_jobs_json.append(job_structure)

        # 2. GENERAR FASTA (Formato Copy-Paste con '/')
        # Estructura: >Nombre
        #             SECUENCIA_BINDER/SECUENCIA_TARGET
        fasta_path = os.path.join(BATCH_FASTA_DIR, f"{design_name}.fasta")
        
        complex_sequence = f"{binder_seq}/{PDL1_SEQUENCE}"
        
        with open(fasta_path, "w") as f:
            f.write(f">{design_name}\n{complex_sequence}\n")

        # Marcar como listo
        df.at[idx, 'status'] = 'ready_for_google'

    # Guardar JSON
    json_output_path = os.path.join(AF_INPUT_DIR, f"upload_to_google_{timestamp}.json")
    with open(json_output_path, "w") as jf:
        json.dump(all_jobs_json, jf, indent=4)

    # Actualizar CSV
    df.to_csv(HISTORY_FILE, index=False)
    
    print("-" * 60)
    print(f"✅ ¡PROCESO COMPLETADO!")
    print(f"📂 FASTAs listos para copiar (con '/'): {BATCH_FASTA_DIR}")
    print(f"📂 JSON listo para subir: {json_output_path}")
    print("-" * 60)

if __name__ == "__main__":
    prepare_package()