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

import os
import json
import glob

# --- CONFIGURACIÓN ---
run_name = "lote1" # Debe coincidir con el nombre de carpeta del paso anterior

# Rutas relativas (Automáticas)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
mpnn_output_dir = os.path.join(project_root, "outputs", "02_proteinmpnn", run_name, "seqs")
output_json = os.path.join(project_root, "outputs", "03_alphafold_inputs", f"{run_name}_jobs.json")

# --- SECUENCIA DE PD-1 (IMPORTANTE) ---
# Esta es la secuencia de la Cadena A de tu estructura 4ZQK (PD-1).
# AlphaFold necesita saber qué es el "Target".
pd1_sequence = "PGWFLDSPDRPWNPPTFSPALLVVTEGDNATFTCSFSNTSESFVLNWYRMSPSNQTDKLAAFPEDRSQPGQDCRFRVTQLPNGRDFHMSVVRARRNDSGTYLCGAISLAPKAQIKESLRAELRVTERRAEVPTAHPSPSPRPAGQFQTLVV"

jobs = []

# Buscar todos los archivos .fa (FASTA)
fasta_files = glob.glob(os.path.join(mpnn_output_dir, "*.fa"))
print(f"--> Procesando {len(fasta_files)} diseños encontrados en: {mpnn_output_dir}")

for fasta_file in fasta_files:
    try:
        with open(fasta_file, 'r') as f:
            lines = f.readlines()
            # El formato de MPNN suele poner las secuencias en la última línea
            # Ejemplo: SECUENCIA_PD1/SECUENCIA_BINDER
            seq_line = lines[-1].strip()
            
            if "/" in seq_line:
                parts = seq_line.split("/")
                # Asumimos: Parte 0 = PD-1 (Ya la tenemos), Parte 1 = Binder (La nueva)
                binder_seq = parts[1] 
            else:
                print(f"⚠️  Saltando {os.path.basename(fasta_file)}: Formato desconocido")
                continue
                
        # Construir la estructura JSON que pide AlphaFold Server
        job_name = os.path.basename(fasta_file).replace(".fa", "")
        
        job = {
            "name": job_name,
            "modelSeeds": [], # Semilla aleatoria
            "sequences": [
                {
                    "proteinChain": {
                        "sequence": pd1_sequence,
                        "count": 1
                    }
                },
                {
                    "proteinChain": {
                        "sequence": binder_seq, # La secuencia diseñada
                        "count": 1
                    }
                }
            ]
        }
        jobs.append(job)
        
    except Exception as e:
        print(f"Error procesando {fasta_file}: {e}")

# Guardar el archivo final
os.makedirs(os.path.dirname(output_json), exist_ok=True)
with open(output_json, 'w') as f:
    json.dump(jobs, f, indent=4)

print(f"\n✅ ¡ÉXITO! JSON generado: {output_json}")
print("--> Siguiente paso: Sube este archivo a https://alphafoldserver.com/submit")
