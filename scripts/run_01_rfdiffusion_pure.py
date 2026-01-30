#!/usr/bin/env python3
# =============================================================================
# SCRIPT 01: RFdiffusion - V51 "SPLIT CONTIG FIX"
# =============================================================================
# Fix: KeyError: 'receptor_con_ref_pdb_idx'.
# Cause: The model failed to identify the "Receptor" in the mapping dict.
# Solution: Pass contigs as a SPLIT list ['Target/0', 'Binder'] instead of
#           a merged string. This forces correct Receptor/Binder classification.
# =============================================================================

import os
import sys
import subprocess
import urllib.request
import json
from datetime import datetime

# --- CONFIGURACIÓN ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RFDIFFUSION_DIR = os.path.expanduser("~/herramientas/RFdiffusion") 
OUTPUT_BASE = os.path.join(PROJECT_ROOT, "outputs", "01_rfdiffusion")
BATCH_ID = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
OUTPUT_DIR = os.path.join(OUTPUT_BASE, BATCH_ID)

AF2_RAW = os.path.join(PROJECT_ROOT, "data", "processed_pdbs", "AF2_raw_v51.pdb")
FINAL_PDB = os.path.join(PROJECT_ROOT, "data", "processed_pdbs", "Target_Fixed_A1.pdb")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(AF2_RAW), exist_ok=True)

print(f"🚀 INICIANDO V51 (SPLIT CONTIG FIX) - {BATCH_ID}")

# =============================================================================
# PASO 1: PREPARAR PDB (Misma lógica robusta V50)
# =============================================================================
if not os.path.exists(FINAL_PDB): # Si ya existe el bueno, lo usamos
    print("⚙️  Regenerando PDB desde AlphaFold...")
    # Descargar
    try:
        url = 'https://alphafold.ebi.ac.uk/api/prediction/Q9NZQ7'
        with urllib.request.urlopen(url) as r:
            data = json.load(r)
            urllib.request.urlretrieve(data[0]['pdbUrl'], AF2_RAW)
    except:
        print("❌ Error descargando AF2."); sys.exit(1)

    # Reescribir Fuerza Bruta (A1..120)
    current_res = 0
    last_res = None
    with open(AF2_RAW, 'r') as fin, open(FINAL_PDB, 'w') as fout:
        for line in fin:
            if line.startswith("ATOM"):
                orig = line[22:26]
                if orig != last_res:
                    current_res += 1
                    last_res = orig
                if current_res > 120: break
                fout.write(f"{line[:21]}A{current_res:4d}{line[26:]}")
    print(f"✅ PDB Listo: {FINAL_PDB}")
else:
    print(f"✅ Usando PDB existente: {FINAL_PDB}")

# =============================================================================
# PASO 2: CONSTRUIR COMANDO (CAMBIO CLAVE AQUÍ)
# =============================================================================

# Hotspots limpios (sin espacios)
hotspots = ["A35", "A90"]
hotspot_str = str(hotspots).replace(" ", "").replace('"', "'")

# CONTIG SPLIT: La clave del éxito.
# Usamos una lista de Python real con dos elementos string.
# Hydra lo interpretará como una lista de contigs.
# Elemento 1: "A1-120/0" (Target + Break)
# Elemento 2: "70-70"    (Binder longitud fija)
contig_arg = "['A1-120/0','70-70']" 

cmd = [
    "python3", os.path.join(RFDIFFUSION_DIR, "scripts", "run_inference.py"),
    f"inference.output_prefix={OUTPUT_DIR}/design",
    f"inference.input_pdb={FINAL_PDB}",
    "inference.num_designs=5",
    "inference.deterministic=True",
    "diffuser.T=50",
    f"inference.ckpt_override_path={os.path.join(RFDIFFUSION_DIR, 'models/Base_ckpt.pt')}",
    
    # Argumentos corregidos
    f"contigmap.contigs={contig_arg}",  # Lista explícita separada
    f"ppi.hotspot_res={hotspot_str}"
]

# =============================================================================
# PASO 3: EJECUTAR
# =============================================================================
print("\n🔥 EJECUTANDO RFDIFFUSION...")
print(f"   Contigs: {contig_arg}")
print(f"   Hotspots: {hotspot_str}")
print("-" * 50)

try:
    subprocess.run(cmd, cwd=RFDIFFUSION_DIR, check=True)
    print("\n✅✅ ¡BATCH COMPLETADO CON ÉXITO!")
    print(f"📂 Resultados: {OUTPUT_DIR}")
except subprocess.CalledProcessError as e:
    print(f"\n❌ Error: {e}")