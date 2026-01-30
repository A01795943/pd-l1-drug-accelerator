#!/bin/bash
# =============================================================================
# SCRIPT 02: DISEÑO DE SECUENCIA (AUTOMÁTICO)
# =============================================================================
# OBJETIVO: Detectar la carpeta más reciente de RFdiffusion y diseñar sus secuencias.
# =============================================================================

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
source "$SCRIPT_DIR/env_config.sh"

# --- A. DETECTAR EL ÚLTIMO BATCH ---
# Busca en la carpeta outputs/01_rfdiffusion y ordena por fecha (el más nuevo arriba)
LATEST_BATCH_PATH=$(ls -td "$PROJECT_ROOT/outputs/01_rfdiffusion/batch_"* | head -1)

if [ -z "$LATEST_BATCH_PATH" ]; then
    echo "❌ ERROR: No se encontraron carpetas batch_ en outputs/01_rfdiffusion"
    exit 1
fi

BATCH_NAME=$(basename "$LATEST_BATCH_PATH")

echo "-----------------------------------------------------------"
echo " 🎯 PROCESANDO EL BATCH MÁS RECIENTE: $BATCH_NAME"
echo "-----------------------------------------------------------"

INPUT_DIR="$LATEST_BATCH_PATH"
# Creamos una carpeta espejo en MPNN
OUTPUT_DIR="$PROJECT_ROOT/outputs/02_proteinmpnn/$BATCH_NAME"

mkdir -p "$OUTPUT_DIR"

# --- B. ENTORNO ---
if [ -f "$HOME/miniforge3/etc/profile.d/conda.sh" ]; then
    source "$HOME/miniforge3/etc/profile.d/conda.sh"
fi
conda activate "$CONDA_ENV_NAME"

# --- C. EJECUCIÓN ---
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

# --- D. REGISTRO ---
LOG_FILE="$PROJECT_ROOT/outputs/execution_log.txt"
echo "ProteinMPNN | $BATCH_NAME | Procesado Exitosamente | $(date)" >> "$LOG_FILE"

echo "✅ Secuencias generadas en: $OUTPUT_DIR"