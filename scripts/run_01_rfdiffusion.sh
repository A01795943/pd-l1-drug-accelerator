#!/bin/bash
# =============================================================================
# SCRIPT 01: GENERACIÓN DE ESTRUCTURAS (RFdiffusion)
# =============================================================================
# OBJETIVO:
# Utiliza Inteligencia Artificial Generativa para crear "esqueletos" de proteínas
# (Backbones) que encajen geométricamente en el sitio activo de PD-1.
#
# INPUT:  data/processed_pdbs/pd1_only.pdb (Tu estructura limpia)
# OUTPUT: outputs/01_rfdiffusion/ (Archivos .pdb sin secuencia real)
# =============================================================================

# --- 1. CONFIGURACIÓN DEL ENTORNO (Escalabilidad) ---
# Detectamos dónde estamos para poder importar la configuración personal
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Cargamos tus rutas personales (env_config.sh)
# Si esto falla, es porque no creaste el archivo env_config.sh
source "$SCRIPT_DIR/env_config.sh"

# --- 2. DEFINICIÓN DE RUTAS DEL PROYECTO ---
INPUT_PDB="$PROJECT_ROOT/data/processed_pdbs/pd1_only.pdb"
OUTPUT_DIR="$PROJECT_ROOT/outputs/01_rfdiffusion/diseño_lote1"

# Creamos la carpeta de salida si no existe
mkdir -p "$OUTPUT_DIR"

# --- 3. ACTIVACIÓN DE CONDA ---
# Intentamos activar conda usando las rutas estándar de instalación
if [ -f "$HOME/miniforge3/etc/profile.d/conda.sh" ]; then
    source "$HOME/miniforge3/etc/profile.d/conda.sh"
elif [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/miniconda3/etc/profile.d/conda.sh"
fi

# Activamos el entorno definido en tu env_config.sh (ej. SE3nv)
conda activate "$CONDA_ENV_NAME"

echo "-----------------------------------------------------------"
echo " 🚀 INICIANDO RFDIFFUSION"
echo " Target: PD-1 (Cadena A)"
echo "-----------------------------------------------------------"

# Nos movemos a la carpeta de RFdiffusion para que encuentre sus modelos (.pt)
cd "$RFDIFFUSION_DIR"

# --- 4. EJECUCIÓN DE LA INFERENCIA ---
./scripts/run_inference.py \
    inference.output_prefix="$OUTPUT_DIR/diseño" \
    inference.input_pdb="$INPUT_PDB" \
    inference.num_designs=10 \
    'contigmap.contigs=[A1-130]/0 60-80' \
    'ppi.hotspot_res=[A75,A76,A85]' \
    inference.ckpt_override_path="$RFDIFFUSION_DIR/models/Active_site_ckpt.pt"

# --- GLOSARIO DE BANDERAS (Para tu equipo) ---
# * inference.num_designs=10: Generará 10 opciones diferentes.
# * contigmap.contigs=[A1-130]/0 60-80: 
#      - [A1-130]: Toma la Cadena A (PD-1) residuos 1 al 130 y DÉJALA FIJA.
#      - /0: No dejes espacio (gap) entre cadenas.
#      - 60-80: Crea una NUEVA cadena (Binder) de longitud variable entre 60 y 80 residuos.
# * ppi.hotspot_res=[A75...]: Obliga al binder a tocar estos residuos de PD-1.
# * ckpt_override_path: Usa el modelo especializado en sitios activos (Active_site).

echo "✅ LISTO: Revisa los resultados en $OUTPUT_DIR"
