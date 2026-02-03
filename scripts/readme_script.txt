🧬 Scripts del Pipeline de Diseño de Proteínas

Este directorio contiene los módulos de automatización para el diseño generativo de *binders* de proteínas utilizando **RFdiffusion**, **ProteinMPNN** y **AlphaFold 3**.

El flujo de trabajo es secuencial (00 → 01 → 02 → 03).

---

## 🚀 Guía Rápida de Ejecución

### 0. Configuración Inicial (Solo la primera vez)
Prepara las carpetas, verifica librerías y configura tus claves de API.
```bash
python scripts/run_00_setup_env.py

1️⃣ Generación de Estructuras (Backbones)
Script: run_01_nvidia_api.py Genera los esqueletos de proteínas (PDB) utilizando IA generativa (RFdiffusion).

Entrada: data/references/target_alphafold.pdb (Tu Target limpio).

Salida: Archivos .pdb en outputs/01_diffusion/.

Nota: Requiere NVIDIA_API_KEY.

Bash

python scripts/run_01_nvidia_api.py
2️⃣ Diseño de Secuencia (ProteinMPNN)
Script: run_02_mpnn_local_v2.py Toma los PDBs generados y diseña la secuencia de aminoácidos del Binder.

Funciones Clave:

Incremental: Solo procesa los diseños nuevos que no estén en el historial.

Limpieza: Asegura que el formato de salida sea BINDER / TARGET (elimina linkers basura y estandariza el Target PD-L1).

Salida: Actualiza el archivo data/processed_history.csv.

Bash

python scripts/run_02_mpnn_local_v2.py
3️⃣ Validación (Input para AlphaFold 3)
Script: run_03_alphafold_pipeline_local.py Prepara los archivos necesarios para subir a Google AlphaFold Server.

Funciones Clave:

Genera archivos JSON divididos en lotes de 30 trabajos (Límite diario de cuota gratuita).

Estructura correcta: Separa Binder y Target como entidades distintas.

Salida: Archivos .json y .fasta en outputs/03_alphafold_inputs/.

Bash

python scripts/run_03_alphafold_pipeline_local.py
🛠️ Utilidades Extra
Actualizar Base de Datos (EDA)
Script: update_database.py Escanea todas las carpetas y crea un archivo maestro (MASTER_DB_METADATA.csv) para análisis de datos en Notebooks.

Bash

python scripts/update_database.py
🔐 Configuración de Seguridad (.env)
El archivo .env se encuentra en la raíz del proyecto y contiene tus secretos. ⚠️ IMPORTANTE: Nunca subas este archivo a GitHub.

Debe tener este formato:

Ini, TOML

# API Key de NVIDIA para RFdiffusion
NVIDIA_API_KEY=nvapi-tu-clave-secreta-aqui...

# Ruta local donde instalaste ProteinMPNN
MPNN_PATH=/home/usuario/herramientas/ProteinMPNN


Estructura del prtoyecto
proyecto/
├── .env                       # Variables secretas (NO SUBIR)
├── data/
│   ├── references/            # Aquí va tu target_alphafold.pdb
│   └── processed_history.csv  # Historial de secuencias generadas
├── outputs/
│   ├── 01_diffusion/          # Resultados de RFdiffusion
│   ├── 02_proteinmpnn/        # Resultados de MPNN
│   └── 03_alphafold_inputs/   # Archivos listos para AF3
└── scripts/                   # Todos los scripts de python