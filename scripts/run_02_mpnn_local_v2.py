import os
import subprocess
import torch
import csv
import sys
import glob
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# =============================================================================
# 🚀 PASO 2: PROTEIN MPNN (ESTRATEGIA LIMPIEZA TOTAL)
# =============================================================================

load_dotenv()

# 1. Configuración
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

DIFFUSION_DIR = os.path.join(PROJECT_ROOT, "outputs", "01_diffusion")
OUTPUT_BASE = os.path.join(PROJECT_ROOT, "outputs", "02_proteinmpnn")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
HISTORY_FILE = os.path.join(DATA_DIR, "processed_history.csv")

# 🎯 SECUENCIA TARGET LIMPIA (PD-L1 HUMANO)
# Usamos esta FIJA para evitar traer basura (linkers GGG) de los PDBs
PDL1_CLEAN_SEQ = "MRIFAVFIFMTYWHLLNAFTVTVPKDLYVVEYGSNMTIECKFPVEKQLDLAALIVYWEMEDKNIIQFVHGEEDLKVQHSSYRQRARLLKDQLSLGNAALQITDVKLQDAGVYRCMISYGGADYKRITVKVNAPYNKINQRILVVDPVTSEHELTCQAEGYPKAEVIWTSSDHQVLSGKTTTTNSKREEKLFNVTSTLRINTTTNEIFYCTFRRLDPEENHTAELVIPELPLAHPPNER"

FORCE_RERUN = False # True = Reprocesar todo | False = Solo nuevos

# 2. Configurar MPNN
MPNN_DIR = os.getenv("MPNN_PATH")
if not MPNN_DIR or not os.path.exists(MPNN_DIR):
    POSIBLES = [os.path.join(PROJECT_ROOT, "ProteinMPNN"), os.path.expanduser("~/herramientas/ProteinMPNN")]
    MPNN_DIR = next((r for r in POSIBLES if os.path.exists(r)), None)

def setup_environment():
    if not MPNN_DIR:
        print("❌ ERROR: No encuentro ProteinMPNN. Revisa tu .env")
        sys.exit(1)
    os.makedirs(OUTPUT_BASE, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)

def get_processed_pdbs():
    processed = set()
    if os.path.exists(HISTORY_FILE):
        try:
            df = pd.read_csv(HISTORY_FILE)
            if 'source_pdb' in df.columns:
                processed = set(df['source_pdb'].astype(str).str.strip().tolist())
        except: pass
    return processed

def run_batch():
    setup_environment()
    
    all_pdb_files = sorted(glob.glob(os.path.join(DIFFUSION_DIR, "*.pdb")))
    if not all_pdb_files:
        print(f"❌ No hay PDBs en {DIFFUSION_DIR}")
        return

    # Filtro: Solo procesar lo nuevo
    processed_pdbs = get_processed_pdbs()
    files_to_process = []
    
    if FORCE_RERUN:
        files_to_process = all_pdb_files
        print("⚠️  Modo FORCE_RERUN activado.")
    else:
        for p in all_pdb_files:
            if os.path.basename(p).replace(".pdb", "") not in processed_pdbs:
                files_to_process.append(p)
    
    if not files_to_process:
        print("✅ Todo actualizado. No hay diseños nuevos.")
        return

    BATCH_ID = f"batch_{datetime.now().strftime('%Y%m%d_%H%M')}"
    print(f"🚀 Procesando {len(files_to_process)} diseños (Target Limpio)...")
    
    mpnn_script = os.path.join(MPNN_DIR, "protein_mpnn_run.py")
    success_count = 0

    for i, pdb_path in enumerate(files_to_process, 1):
        pdb_name = os.path.basename(pdb_path).replace(".pdb", "")
        current_output_dir = os.path.join(OUTPUT_BASE, BATCH_ID, pdb_name)
        os.makedirs(current_output_dir, exist_ok=True)

        print(f"🧬 [{i}/{len(files_to_process)}] Diseñando: {pdb_name}")

        cmd = [
            sys.executable, mpnn_script,
            "--pdb_path", pdb_path,
            "--out_folder", current_output_dir,
            "--num_seq_per_target", "8",
            "--sampling_temp", "0.3",
            "--batch_size", "1"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                # Aquí forzamos la secuencia limpia
                save_to_history(current_output_dir, BATCH_ID, pdb_name)
                success_count += 1
            else:
                print(f"❌ Falló MPNN: {result.stderr}")
        except Exception as e:
            print(f"🔥 Error: {e}")

    print("-" * 50)
    print(f"🏁 Finalizado. {success_count} diseños procesados.")

def save_to_history(out_dir, batch_id, original_pdb):
    """
    Guarda la secuencia. SIEMPRE usa la secuencia limpia de PD-L1 como target.
    """
    seqs_folder = os.path.join(out_dir, "seqs")
    if not os.path.exists(seqs_folder): return False

    new_rows = []
    for fa in glob.glob(os.path.join(seqs_folder, "*.fa")):
        with open(fa, "r") as f:
            lines = f.readlines()
            # MPNN .fa output: >Header \n Sequence
            for k in range(1, len(lines), 2):
                raw_seq = lines[k].strip()
                
                # --- LIMPIEZA Y FORMATEO ---
                # 1. Obtenemos solo el Binder (parte izquierda si hubiera slash, o todo si no hay)
                if '/' in raw_seq:
                    binder_only = raw_seq.split('/')[0].strip()
                else:
                    binder_only = raw_seq.strip()
                
                # 2. Reconstruimos con el Target Oficial Limpio
                # Esto elimina las 'GGGG' y asegura que siempre haya '/'
                final_seq_clean = f"{binder_only}/{PDL1_CLEAN_SEQ}"
                # ---------------------------

                new_rows.append([final_seq_clean, datetime.now().isoformat(), batch_id, original_pdb, "waiting_validation"])

    if new_rows:
        file_exists = os.path.exists(HISTORY_FILE)
        with open(HISTORY_FILE, "a", newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["sequence", "date", "batch", "source_pdb", "status"])
            writer.writerows(new_rows)
        return True
    return False

if __name__ == "__main__":
    run_batch()