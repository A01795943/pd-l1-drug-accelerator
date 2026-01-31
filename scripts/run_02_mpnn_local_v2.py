import os
import subprocess
import torch
import csv
import sys
import glob
from datetime import datetime

# =============================================================================
# 🚀 PASO 2: PROTEIN MPNN (MÉTODO SIMPLE DIRECTO)
# =============================================================================

# 1. Configuración de Rutas
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# Rutas de entrada (Tus 40 diseños) y salida
DIFFUSION_DIR = os.path.join(PROJECT_ROOT, "outputs", "01_diffusion")
OUTPUT_BASE = os.path.join(PROJECT_ROOT, "outputs", "02_proteinmpnn")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
HISTORY_FILE = os.path.join(DATA_DIR, "processed_history.csv")

# 2. Buscar ProteinMPNN
POSIBLES_RUTAS = [
    os.path.expanduser("~/herramientas/ProteinMPNN"),
    "/home/subde/herramientas/ProteinMPNN",
    os.path.join(PROJECT_ROOT, "ProteinMPNN")
]
MPNN_DIR = next((r for r in POSIBLES_RUTAS if os.path.exists(r)), None)

def setup_environment():
    if not MPNN_DIR:
        print("❌ ERROR: No encuentro ProteinMPNN.")
        sys.exit(1)
        
    os.makedirs(OUTPUT_BASE, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)

    # Solo informativo, ya que MPNN detecta la GPU solo
    if torch.cuda.is_available():
        print(f"⚡ GPU Detectada: {torch.cuda.get_device_name(0)}")

def run_batch():
    setup_environment()
    
    # 1. Encontrar los archivos PDB
    pdb_files = sorted(glob.glob(os.path.join(DIFFUSION_DIR, "*.pdb")))
    
    if not pdb_files:
        print(f"❌ No encontré archivos .pdb en: {DIFFUSION_DIR}")
        return

    BATCH_ID = f"batch_{datetime.now().strftime('%Y%m%d_%H%M')}"
    print(f"🚀 Procesando {len(pdb_files)} diseños con ProteinMPNN...")
    print(f"📂 Batch ID: {BATCH_ID}")
    print("-" * 50)

    mpnn_script = os.path.join(MPNN_DIR, "protein_mpnn_run.py")
    success_count = 0

    # 2. Bucle simple: Un archivo a la vez, comando directo
    for i, pdb_path in enumerate(pdb_files, 1):
        pdb_name = os.path.basename(pdb_path).replace(".pdb", "")
        
        # Carpeta individual para no mezclar resultados
        current_output_dir = os.path.join(OUTPUT_BASE, BATCH_ID, pdb_name)
        os.makedirs(current_output_dir, exist_ok=True)

        print(f"🧬 [{i}/{len(pdb_files)}] Diseñando: {pdb_name} ...")

        # EL COMANDO QUE SÍ FUNCIONA (Sin --device, con --pdb_path)
        cmd = [
            sys.executable, mpnn_script,
            "--pdb_path", pdb_path,              # <--- Tu método original
            "--out_folder", current_output_dir,
            "--num_seq_per_target", "8",
            "--sampling_temp", "0.1",
            "--batch_size", "1"
        ]
        
        try:
            # Ejecutar y capturar errores si los hay
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                save_to_history(current_output_dir, BATCH_ID, pdb_name)
                success_count += 1
            else:
                print(f"❌ Error en {pdb_name}:")
                print(result.stderr) # Muestra el error real si falla

        except Exception as e:
            print(f"🔥 Error crítico: {e}")

    print("-" * 50)
    print(f"🏁 Finalizado: {success_count}/{len(pdb_files)} diseños exitosos.")

def save_to_history(out_dir, batch_id, original_pdb):
    """Guarda las secuencias generadas en el CSV."""
    seqs_folder = os.path.join(out_dir, "seqs")
    if not os.path.exists(seqs_folder): return

    new_rows = []
    # Buscar cualquier .fa generado
    for fa in glob.glob(os.path.join(seqs_folder, "*.fa")):
        with open(fa, "r") as f:
            lines = f.readlines()
            for k in range(1, len(lines), 2):
                seq = lines[k].strip()
                # Status listo para el Paso 3
                new_rows.append([seq, datetime.now().isoformat(), batch_id, original_pdb, "waiting_validation"])

    if new_rows:
        file_exists = os.path.exists(HISTORY_FILE)
        with open(HISTORY_FILE, "a", newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["sequence", "date", "batch", "source_pdb", "status"])
            writer.writerows(new_rows)

if __name__ == "__main__":
    run_batch()