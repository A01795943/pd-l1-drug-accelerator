#!/bin/bash
# =============================================================================
# SCRIPT 01: RFdiffusion - CLEAN DATA MODE (V10)
# =============================================================================
# Fix: SVD crash due to dirty PDB (ANISOU/HETATM).
# Input: pd1_clean.pdb (Only Protein Atoms)
# =============================================================================

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
source "$SCRIPT_DIR/env_config.sh"

# --- 1. PROTECCIONES DE GPU ---
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128
export TORCH_ALLOW_TF32_CUBLAS_OVERRIDE=0
export TORCH_CUDNN_ALLOW_TF32=0
# Determinismo estricto para evitar errores matemáticos
export CUBLAS_WORKSPACE_CONFIG=:4096:8

# --- 2. CONFIGURACIÓN ---
BATCH_ID="batch_$(date +%Y%m%d_%H%M%S)"

# CAMBIO IMPORTANTE: Usamos el archivo LIMPIO
INPUT_PDB="$PROJECT_ROOT/data/processed_pdbs/pd1_clean.pdb"

OUTPUT_DIR="$PROJECT_ROOT/outputs/01_rfdiffusion/$BATCH_ID"
LOG_FILE="$PROJECT_ROOT/outputs/execution_log.txt"

mkdir -p "$OUTPUT_DIR"

# --- 3. ENTORNO ---
source "$HOME/miniforge3/etc/profile.d/conda.sh" 2>/dev/null || source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate "$CONDA_ENV_NAME"

echo "-----------------------------------------------------------"
echo " 🚀 INICIANDO BATCH: $BATCH_ID"
echo " 🧹 Input: pd1_clean.pdb (Sin agua/iones)"
echo " 🛡️  Modo: Safe Deterministic"
echo "-----------------------------------------------------------"

cd "$RFDIFFUSION_DIR"

# --- 4. EJECUCIÓN ---
./scripts/run_inference.py \
    inference.output_prefix="'$OUTPUT_DIR/design'" \
    inference.input_pdb="'$INPUT_PDB'" \
    inference.num_designs=40 \
    inference.deterministic=True \
    'contigmap.contigs=["A18-132/0 60-80"]' \
    'ppi.hotspot_res=[A75,A76,A85]' \
    inference.ckpt_override_path="'$RFDIFFUSION_DIR/models/Active_site_ckpt.pt'"

# --- 5. REGISTRO ---
echo "RFdiffusion | $BATCH_ID | 40 Diseños | $(date)" >> "$LOG_FILE"
echo "✅ Batch completado."