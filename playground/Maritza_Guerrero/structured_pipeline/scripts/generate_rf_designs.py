import os
from pathlib import Path
import subprocess
import logging

# Configuración básica
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RFdiffusion_runner")

# --- Configuración de entrada ---
PDB_ID = "6B3J"  # Aquí puedes poner cualquier PDB
CHAIN_TO_REMOVE = "P"  # si aplica
NUM_DESIGNS = 100  # cuántas estructuras quieres generar
ITERATIONS = 30
HOTSPOTS = ["R312", "R313", "R314", "R315"]  # ejemplo
CONTIGS = "12-15/0 R311-337"
VISUAL = "image"

# --- Rutas ---
BASE_DIR = Path.cwd()
OUTPUT_DIR = BASE_DIR / "rfdiffusion_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
PDB_PATH = OUTPUT_DIR / f"{PDB_ID}.pdb"
RF_SCRIPT = Path("/workspace/RFdiffusion/scripts/run_inference.py")  # ajustar según tu repo

# --- Descargar PDB si no existe ---
if not PDB_PATH.exists():
    import urllib.request
    url = f"https://files.rcsb.org/download/{PDB_ID}.pdb"
    logger.info(f"Descargando PDB {PDB_ID}...")
    urllib.request.urlretrieve(url, PDB_PATH)
    logger.info(f"PDB guardado en {PDB_PATH}")

# --- Preparar parámetros para Hydra ---
hotspot_value = "[" + ",".join(HOTSPOTS) + "]"
contigs_value = CONTIGS  # sin comillas extras

# --- Loop para generar N diseños ---
for i in range(NUM_DESIGNS):
    design_output = OUTPUT_DIR / f"design_{i}"
    design_output.mkdir(exist_ok=True)
    
    command = (
        f"PYTHONPATH=/workspace/RFdiffusion python3 {RF_SCRIPT} "
        f"+experiment.name=design_{i} "
        f"+pdb.source={PDB_PATH} "
        f"+rfdiffusion.contigs={contigs_value} "
        f"+rfdiffusion.hotspot={hotspot_value} "
        f"+rfdiffusion.iterations={ITERATIONS} "
        f"+rfdiffusion.num_designs=1 "  # generar 1 diseño por iteración
        f"+rfdiffusion.visual={VISUAL} "
        f"+rfdiffusion.output_dir={design_output}"
    )
    
    logger.info(f"Ejecutando RFdiffusion diseño {i}: {command}")
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"RFdiffusion falló en diseño {i}: {e}")
        continue

logger.info(f"Generación completada. Los diseños están en {OUTPUT_DIR}")
