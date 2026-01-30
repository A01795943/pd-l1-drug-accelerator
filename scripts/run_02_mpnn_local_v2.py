import os
import subprocess
import torch
import csv
import sys
from datetime import datetime

# =============================================================================
# 🚀 DETECCIÓN AUTOMÁTICA DE RUTAS (Estilo Absoluto Dinámico)
# =============================================================================

# 1. Detectar la raíz del proyecto (sube un nivel desde 'scripts/')
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# 2. Intentar encontrar ProteinMPNN automáticamente
# Buscamos en '~/herramientas' o en un nivel arriba del proyecto
POSIBLES_RUTAS_MPNN = [
    os.path.expanduser("~/herramientas/ProteinMPNN"),
    os.path.join(os.path.dirname(PROJECT_ROOT), "herramientas", "ProteinMPNN"),
    os.path.join(PROJECT_ROOT, "herramientas", "ProteinMPNN")
]

MPNN_DIR = next((ruta for ruta in POSIBLES_RUTAS_MPNN if os.path.exists(ruta)), None)

# 3. Construcción de Rutas del Proyecto (Dinámicas)
INPUT_PDB = os.path.join(PROJECT_ROOT, "outputs", "nvidia_results", "design_nvidia_final.pdb")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
HISTORY_FILE = os.path.join(DATA_DIR, "processed_history.csv")

# Salida organizada
BATCH_ID = f"mpnn_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "outputs", "02_proteinmpnn", BATCH_ID)

# =============================================================================

def setup_environment():
    """Asegura que las carpetas necesarias existan."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    
    if not MPNN_DIR:
        print("❌ ERROR: No se encontró la carpeta de ProteinMPNN.")
        print("Asegúrate de que esté en ~/herramientas/ProteinMPNN")
        sys.exit(1)
    
    if not os.path.exists(INPUT_PDB):
        print(f"❌ ERROR: No se encontró el archivo de entrada:\n   {INPUT_PDB}")
        sys.exit(1)

def load_history():
    seen = set()
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            reader = csv.reader(f)
            next(reader, None) # Saltar header
            for row in reader:
                if row: seen.add(row[0])
    return seen

def run_mpnn():
    setup_environment()
    history = load_history()
    
    print(f"🌟 Proyecto: {os.path.basename(PROJECT_ROOT)}")
    print(f"🤖 Usando ProteinMPNN en: {MPNN_DIR}")
    print(f"⚙️  Dispositivo: {torch.cuda.get_device_name(0)}")
    
    script_path = os.path.join(MPNN_DIR, "protein_mpnn_run.py")
    
    cmd = [
        "python3", script_path,
        "--pdb_path", INPUT_PDB,
        "--out_folder", OUTPUT_DIR,
        "--num_seq_per_target", "10",
        "--sampling_temp", "0.1",
        "--device", "cuda:0"
    ]
    
    try:
        # Ejecutar y capturar salida
        subprocess.run(cmd, check=True)
        
        # Procesar resultados y filtrar
        process_results(history)
        
    except Exception as e:
        print(f"❌ Fallo en la ejecución: {e}")

def process_results(history):
    seqs_path = os.path.join(OUTPUT_DIR, "seqs")
    fa_files = [f for f in os.listdir(seqs_path) if f.endswith(".fa")]
    
    if not fa_files:
        print("⚠️ No se generaron archivos de secuencia.")
        return

    fa_file = os.path.join(seqs_path, fa_files[0])
    new_entries = []

    with open(fa_file, "r") as f:
        lines = f.readlines()
        # ProteinMPNN FASTA: >Header\nSequence\n...
        for i in range(1, len(lines), 2):
            seq = lines[i].strip()
            if seq not in history:
                new_entries.append([seq, datetime.now().isoformat(), BATCH_ID])

    if new_entries:
        file_exists = os.path.exists(HISTORY_FILE)
        with open(HISTORY_FILE, "a", newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["sequence", "date", "batch"])
            writer.writerows(new_entries)
        print(f"✅ ¡Éxito! {len(new_entries)} secuencias nuevas registradas.")
    else:
        print("♻️  Todas las secuencias generadas ya existían en el historial.")

if __name__ == "__main__":
    run_mpnn()