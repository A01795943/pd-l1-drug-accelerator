#!/bin/bash
# =============================================================================
# SCRIPT 01: RFdiffusion - "JUST MAKE IT WORK" (V45)
# =============================================================================
# Goal: Bypass all CLI syntax errors and Input PDB issues.
# Step 1: Unconditional generation (Sanity Check).
# Step 2: AlphaFold Target + Python-injected Hotspots (The Fix).
# =============================================================================

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
source "$SCRIPT_DIR/env_config.sh"

export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128
export CUBLAS_WORKSPACE_CONFIG=:4096:8

BATCH_ID="batch_$(date +%Y%m%d_%H%M%S)"
OUTPUT_DIR="$PROJECT_ROOT/outputs/01_rfdiffusion/$BATCH_ID"
AF2_PDB="$PROJECT_ROOT/data/processed_pdbs/AF2_auto_v45.pdb"
CLEAN_PDB="$PROJECT_ROOT/data/processed_pdbs/AF2_ready_v45.pdb"
LAUNCHER="$PROJECT_ROOT/outputs/launcher_v45.sh"

mkdir -p "$OUTPUT_DIR"
source "$HOME/miniforge3/etc/profile.d/conda.sh" 2>/dev/null || source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate "$CONDA_ENV_NAME"

echo "-----------------------------------------------------------"
echo " 🩺 PASO 1: PRUEBA DE VIDA (GENERACIÓN SIMPLE)"
echo "    Si esto falla, el problema es tu PC/Instalación."
echo "-----------------------------------------------------------"

cd "$RFDIFFUSION_DIR"

# Generamos 1 diseño pequeño sin target. Esto SIEMPRE debe funcionar.
./scripts/run_inference.py \
    inference.output_prefix="$OUTPUT_DIR/sanity_check" \
    inference.num_designs=1 \
    'contigmap.contigs=["100-100"]' \
    diffuser.T=20

if [ $? -ne 0 ]; then
    echo "❌ ERROR CRÍTICO: RFdiffusion no puede generar ni siquiera una proteína simple."
    echo "   Tu instalación de CUDA/PyTorch está corrupta."
    exit 1
else
    echo "✅ ¡PRUEBA DE VIDA SUPERADA! Tu sistema funciona."
fi

echo "-----------------------------------------------------------"
echo " 🚀 PASO 2: DISEÑO PD-L1 (ALPHAFOLD + HOTSPOTS BLINDADOS)"
echo "    Usando estructura perfecta y sintaxis inyectada."
echo "-----------------------------------------------------------"

# 1. DESCARGA DINÁMICA DE ALPHAFOLD (Evita error 404)
echo "⬇️  Obteniendo estructura AlphaFold..."
python3 -c "
import urllib.request, json, os
try:
    url = 'https://alphafold.ebi.ac.uk/api/prediction/Q9NZQ7'
    with urllib.request.urlopen(url) as r:
        data = json.load(r)
        pdb_url = data[0]['pdbUrl']
        urllib.request.urlretrieve(pdb_url, '$AF2_PDB')
    print('✅ Descarga OK')
except Exception as e:
    print(f'❌ Error descarga: {e}')
"

if [ ! -s "$AF2_PDB" ]; then echo "❌ Falló la descarga de AF2."; exit 1; fi

# 2. LIMPIEZA Y PREPARACIÓN (Python puro)
echo "⚙️  Preparando PDB..."
python3 -c "
from Bio.PDB import PDBParser, PDBIO, Chain, Model, Structure
parser = PDBParser(QUIET=True)
s = parser.get_structure('X', '$AF2_PDB')
# Tomamos los primeros 120 residuos (Dominio IgV)
residues = [r for r in s[0]['A'] if r.id[0]==' '][:120]
# Renumerar 1..N
for i, r in enumerate(residues): r.id = (' ', i+1, ' ')

# Guardar
c = Chain.Chain('A'); c.child_list = residues
for r in residues: r.parent = c
m = Model.Model(0); m.add(c); st = Structure.Structure('N'); st.add(m)
io = PDBIO(); io.set_structure(st); io.save('$CLEAN_PDB')
print(f'✅ PDB Listo: 1-{len(residues)} residuos')
"

# 3. GENERAR COMANDO DE LANZAMIENTO (SIN ERRORES DE BASH)
# Aquí escribimos el comando exacto en un archivo .sh para que Bash no se coma las comillas.
# Hotspots clave para PD-L1: A54, A121 (Tyrosinas clave)
cat << EOF > "$LAUNCHER"
#!/bin/bash
cd $RFDIFFUSION_DIR
./scripts/run_inference.py \\
    inference.output_prefix="$OUTPUT_DIR/design" \\
    inference.input_pdb="$CLEAN_PDB" \\
    inference.num_designs=5 \\
    inference.deterministic=True \\
    'contigmap.contigs=["A1-120/0 70-70"]' \\
    'ppi.hotspot_res=["A54", "A121"]' \\
    inference.ckpt_override_path="$RFDIFFUSION_DIR/models/Base_ckpt.pt" \\
    diffuser.T=50
EOF

chmod +x "$LAUNCHER"
"$LAUNCHER"

echo "✅ PROCESO FINALIZADO. Revisa la carpeta outputs."