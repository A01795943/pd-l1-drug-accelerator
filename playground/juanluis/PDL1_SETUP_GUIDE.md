# Guía de Configuración para Pipeline de Agonistas de PD-L1

## Requisitos Previos

### 1. RF Diffusion (NVIDIA NIM API)

**Pasos:**
1. Crear cuenta en [NVIDIA Build](https://build.nvidia.com/)
2. Obtener API key gratuita para desarrollo
3. La API está disponible en: `https://health.api.nvidia.com/v1/biology/ipd/rfdiffusion`

**Instalación:**
```bash
pip install requests
```

**Uso:**
```python
from src.rf_diffusion_generator import RFDiffusionGenerator

generator = RFDiffusionGenerator(api_key="TU_API_KEY")
result = generator.generate_structure(contigs="A1-50")
```

### 2. Protein MPNN

**Opción A: Instalación vía pip (Recomendado)**
```bash
pip install protein-mpnn-pip
```

**Opción B: Instalación desde GitHub**
```bash
git clone https://github.com/dauparas/ProteinMPNN.git
cd ProteinMPNN
# Seguir instrucciones de instalación
```

**Opción C: Docker**
```bash
docker pull cyrusbiotechnology/proteinmpnn
```

**Uso:**
```python
from src.protein_mpnn_generator import ProteinMPNNGenerator

generator = ProteinMPNNGenerator(use_pip=True)
sequences_df = generator.generate_sequences(
    pdb_file="structure.pdb",
    num_designs=10
)
```

### 3. AlphaFold3

**IMPORTANTE**: AlphaFold3 requiere:
- Solicitar acceso a Google DeepMind para obtener parámetros del modelo (~250 GB)
- GPU con al menos 16GB de VRAM recomendado

**Pasos:**
1. Solicitar acceso en: https://github.com/google-deepmind/alphafold3
2. Completar el formulario de acceso
3. Descargar parámetros del modelo una vez aprobado
4. Instalar dependencias según documentación oficial

**Instalación:**
```bash
git clone https://github.com/google-deepmind/alphafold3.git
cd alphafold3
# Seguir instrucciones en docs/installation.md
```

**Uso:**
```python
from src.alphafold3_predictor import AlphaFold3Predictor

predictor = AlphaFold3Predictor(
    alphafold3_path="/ruta/a/alphafold3/run_alphafold3.py",
    model_params_dir="/ruta/a/alphafold3/params"
)

result = predictor.predict_structure(
    sequence="MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVVHSLAKWKRQTLGQHDFSAGEGLYTHMKALRPDEDRLSPLHSVYVDQWDWERVMGDGERQFSTLKSTVEAIWAGIKATEAAVSEEFGLAPFLPDQIHFVHSQELLSRYPDLDAKGRERAIAKDLGAVFLVGIGGKLSDGHRHDVRAPDYDDWSTPSELGHAGLNGDILVWNPVLEDAFELSSMGIRVDADTLKHQLALTGDEDRLELEWHQALLRGEMPQTIGGGIGQSRLTMLLLQLPHIGQVQAGVWPAAVRESVPSLL",
    sequence_id="test_sequence"
)
```

## Estructura de Datos Necesaria

### Archivo PDB de PD-L1

Necesitas una estructura de PD-L1 en formato PDB. Puedes obtenerla de:
- **PDB**: https://www.rcsb.org/ (buscar "PD-L1" o "CD274")
- **AlphaFold DB**: https://alphafold.ebi.ac.uk/ (ID: PDB o UniProt)

**Ejemplo de búsqueda:**
```python
# Descargar estructura de PD-L1 desde PDB
# PDB ID común: 5J8O, 5J89, etc.
```

## Configuración del Proyecto

1. **Crear directorios necesarios:**
```python
from pathlib import Path

data_dir = Path("data")
raw_data_dir = data_dir / "raw"
processed_data_dir = data_dir / "processed"
pdl1_dir = processed_data_dir / "pdl1_agonists"

pdl1_dir.mkdir(parents=True, exist_ok=True)
```

2. **Configurar variables de entorno (opcional):**
```bash
export NVIDIA_API_KEY="tu_api_key"
export ALPHAFOLD3_PATH="/ruta/a/alphafold3"
export PROTEIN_MPNN_PATH="/ruta/a/protein_mpnn"
```

## Flujo de Trabajo Recomendado

1. **Preparación de Datos**
   - Obtener estructura PDB de PD-L1
   - Preparar secuencias de referencia (si las hay)

2. **Generación con RF Diffusion**
   - Generar 5-10 estructuras de binders de diferentes longitudes
   - Guardar estructuras PDB generadas

3. **Diseño de Secuencias con Protein MPNN**
   - Para cada estructura, generar 20-50 secuencias
   - Total: 100-500 secuencias candidatas

4. **Validación con AlphaFold3**
   - Predecir estructura de cada secuencia generada
   - Comparar con estructura original (RMSD, etc.)

5. **Análisis y Filtrado**
   - Calcular descriptores moleculares
   - Evaluar propiedades farmacológicas
   - Filtrar mejores candidatos

6. **Docking Molecular** (Opcional)
   - Predecir afinidad con PD-L1
   - Análisis de interacciones

## Troubleshooting

### Error: "API key inválida" (RF Diffusion)
- Verifica que tu API key sea correcta
- Asegúrate de tener créditos disponibles en NVIDIA Build

### Error: "Protein MPNN no encontrado"
- Verifica la instalación: `pip list | grep protein`
- Si usas CLI, verifica la ruta al ejecutable

### Error: "AlphaFold3 requiere parámetros del modelo"
- Debes solicitar acceso a Google DeepMind
- Descargar parámetros del modelo (~250 GB)
- Verificar que la ruta a los parámetros sea correcta

### Error: "Out of memory" (AlphaFold3)
- Reduce el batch size
- Usa GPU con más VRAM
- Considera usar AlphaFold3 en un servidor remoto

## Recursos Adicionales

- **RF Diffusion Docs**: https://docs.nvidia.com/nim/bionemo/rfdiffusion/
- **Protein MPNN Paper**: https://www.science.org/doi/10.1126/science.add2187
- **AlphaFold3 Paper**: https://www.nature.com/articles/s41586-024-07487-w
- **PD-L1 en PDB**: https://www.rcsb.org/search?q=PD-L1
