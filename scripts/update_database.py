"""
SCRIPT: RECOLECTOR DE DATOS PARA EDA
------------------------------------
Escanea TODAS las carpetas batch de RFdiffusion y ProteinMPNN y crea un 
archivo CSV Maestro con todos los datos.
Usa este CSV en tus Notebooks para analizar tus miles de estructuras.
"""

import os
import pandas as pd
import glob
import time

# Rutas
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rfdiffusion_path = os.path.join(project_root, "outputs", "01_rfdiffusion_results")
mpnn_path = os.path.join(project_root, "outputs", "02_proteinmpnn")
db_path = os.path.join(project_root, "data", "MASTER_DB_METADATA.csv")

data_records = []

# Buscar batches
batches = [d for d in os.listdir(rfdiffusion_path) if d.startswith("batch_")]
print(f"🔄 Escaneando {len(batches)} lotes históricos...")

for batch in batches:
    pdb_folder = os.path.join(rfdiffusion_path, batch)
    mpnn_folder = os.path.join(mpnn_path, batch, "seqs")
    
    # Obtener fecha del batch desde el nombre
    try:
        timestamp_str = batch.replace("batch_", "")
        # Formato simple para el CSV
    except:
        timestamp_str = "unknown"

    pdbs = glob.glob(os.path.join(pdb_folder, "*.pdb"))
    
    for pdb_file in pdbs:
        design_name = os.path.basename(pdb_file).replace(".pdb", "")
        # Buscar secuencias asociadas
        fasta_file = os.path.join(mpnn_folder, f"{design_name}.fa")
        
        has_sequence = os.path.exists(fasta_file)
        
        # Agregar al registro
        data_records.append({
            "batch_id": batch,
            "timestamp": timestamp_str,
            "design_name": design_name,
            "path_pdb": pdb_file,
            "path_fasta": fasta_file if has_sequence else None,
            "status": "Ready for AlphaFold" if has_sequence else "Structure Only"
        })

# Guardar
df = pd.DataFrame(data_records)
df.to_csv(db_path, index=False)

print(f"📊 Base de Datos Actualizada: {len(df)} registros totales.")
print(f"💾 Guardada en: {db_path}")
