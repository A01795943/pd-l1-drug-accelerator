"""
=============================================================================
SCRIPT 03: PREPARACIÓN PARA ALPHAFOLD 3 (Google Server)
=============================================================================
OBJETIVO:
Lee los archivos FASTA generados por ProteinMPNN y crea un único archivo JSON 
que puedes subir directamente a https://alphafoldserver.com/

INPUT:  Archivos .fasta en outputs/02_proteinmpnn/
OUTPUT: Un archivo .json en outputs/03_alphafold_inputs/
=============================================================================
"""
"""
SCRIPT 03: PREPARACIÓN PARA ALPHAFOLD 3 (MODO INTELIGENTE)
----------------------------------------------------------
1. Detecta automáticamente el último batch generado por MPNN.
2. Lee automáticamente la secuencia de PD-1 del archivo PDB (sin copiar/pegar).
3. Genera el JSON para subir a Google.
"""

import os
import json
import glob
from Bio import PDB
from Bio.SeqUtils import seq1

# --- CONFIGURACIÓN AUTOMÁTICA ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

# Rutas clave
pd1_pdb_path = os.path.join(project_root, "data", "processed_pdbs", "pd1_only.pdb")
mpnn_base_dir = os.path.join(project_root, "outputs", "02_proteinmpnn")
af3_output_dir = os.path.join(project_root, "outputs", "03_alphafold_inputs")

# --- 1. ENCONTRAR EL ÚLTIMO BATCH ---
try:
    # Buscar carpetas que empiecen con 'batch_'
    batches = glob.glob(os.path.join(mpnn_base_dir, "batch_*"))
    # Ordenar por fecha de modificación (el más nuevo al final)
    latest_batch = max(batches, key=os.path.getmtime)
    batch_name = os.path.basename(latest_batch)
    mpnn_seqs_dir = os.path.join(latest_batch, "seqs")
    print(f"--> Batch detectado: {batch_name}")
except ValueError:
    print("❌ ERROR: No se encontraron carpetas batch en outputs/02_proteinmpnn/")
    exit(1)

# --- 2. LEER SECUENCIA REAL DE PD-1 (BIOPYTHON) ---
def get_sequence_from_pdb(pdb_path, chain_id="A"):
    parser = PDB.PDBParser(QUIET=True)
    structure = parser.get_structure("target", pdb_path)
    sequence = ""
    for model in structure:
        for chain in model:
            if chain.get_id() == chain_id:
                for residue in chain:
                    if residue.id[0] != " ": continue
                    sequence += seq1(residue.get_resname())
                return sequence
    return ""

print(f"--> Leyendo secuencia nativa de: {pd1_pdb_path}")
pd1_sequence = get_sequence_from_pdb(pd1_pdb_path, chain_id="A")

if not pd1_sequence:
    print("❌ ERROR: No se pudo leer la secuencia de PD-1. Revisa el archivo PDB.")
    exit(1)

# --- 3. GENERAR JSON ---
jobs = []
fasta_files = glob.glob(os.path.join(mpnn_seqs_dir, "*.fa"))
print(f"--> Procesando {len(fasta_files)} diseños para AlphaFold...")

# LIMITADOR (Opcional): Si tienes muchos, solo toma los primeros 20 para no saturar Google
# fasta_files = fasta_files[:20] 

for fasta_file in fasta_files:
    try:
        with open(fasta_file, 'r') as f:
            lines = f.readlines()
            seq_line = lines[-1].strip()
            if "/" in seq_line:
                binder_seq = seq_line.split("/")[1]
            else:
                continue
                
        job_name = f"{batch_name}_{os.path.basename(fasta_file).replace('.fa', '')}"
        
        job = {
            "name": job_name,
            "modelSeeds": [],
            "sequences": [
                {"proteinChain": {"sequence": pd1_sequence, "count": 1}},
                {"proteinChain": {"sequence": binder_seq, "count": 1}}
            ]
        }
        jobs.append(job)
    except Exception as e:
        print(f"Saltando {fasta_file}: {e}")

output_json = os.path.join(af3_output_dir, f"{batch_name}_jobs.json")
os.makedirs(os.path.dirname(output_json), exist_ok=True)

with open(output_json, 'w') as f:
    json.dump(jobs, f, indent=4)

print(f"✅ JSON generado: {output_json}")