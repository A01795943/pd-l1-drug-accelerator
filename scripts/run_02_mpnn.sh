#!/bin/bash
# =============================================================================
# SCRIPT 02: DISEÑO DE SECUENCIA (ProteinMPNN)
# =============================================================================
# OBJETIVO:
# Toma los esqueletos vacíos del paso anterior y les asigna una secuencia de 
# aminoácidos real y soluble, respetando la estructura de PD-1.
#
# INPUT:  outputs/01_rfdiffusion/ (Archivos .pdb)
# OUTPUT: outputs/02_proteinmpnn/ (Archivos .fasta y .pdb completos)
# =============================================================================

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
source "$SCRIPT_DIR/env_config.sh"

# --- 1. RUTAS ---
INPUT_DIR="$PROJECT_ROOT/outputs/01_rfdiffusion/diseño_lote1"
OUTPUT_DIR="$PROJECT_ROOT/outputs/02_proteinmpnn/lote1"

mkdir -p "$OUTPUT_DIR"

# --- 2. ENTORNO ---
# Activamos Conda (MPNN usa PyTorch, igual que el paso anterior)
if [ -f "$HOME/miniforge3/etc/profile.d/conda.sh" ]; then
    source "$HOME/miniforge3/etc/profile.d/conda.sh"
fi
conda activate "$CONDA_ENV_NAME"

echo "-----------------------------------------------------------"
echo " 🧬 INICIANDO PROTEINMPNN"
echo " Objetivo: Diseñar secuencia para Cadena B (Binder)"
echo "-----------------------------------------------------------"

# --- 3. EJECUCIÓN ---
python "$MPNN_DIR/protein_mpnn_run.py" \
    --pdb_path "$INPUT_DIR" \
    --pdb_path_chains "A B" \
    --out_folder "$OUTPUT_DIR" \
    --num_seq_per_target 2 \
    --sampling_temp "0.1" \
    --seed 37 \
    --batch_size 1 \
    --chains_to_design "B" \
    --fixed_chains "A" 

# --- GLOSARIO DE BANDERAS ---
# * pdb_path_chains "A B": El PDB de entrada tiene dos cadenas: A (PD-1) y B (Binder).
# * chains_to_design "B": "Solo inventa secuencia para la Cadena B".
# * fixed_chains "A": "NO TOQUES la secuencia de PD-1 (Cadena A)".
# * sampling_temp "0.1": Temperatura baja = Diseños más conservadores y seguros.
# * num_seq_per_target 2: Por cada esqueleto, genera 2 variantes de secuencia.

echo "✅ LISTO: Secuencias generadas en $OUTPUT_DIR"
