==============================================================================
           GUÍA DE EJECUCIÓN DEL PIPELINE (LEER ANTES DE EMPEZAR)
==============================================================================

Este directorio contiene los scripts automatizados para el diseño de fármacos 
(Binders para PD-1/PD-L1). 

Para que estos scripts funcionen en TU computadora, debes seguir el Paso 0 
obligatoriamente.

------------------------------------------------------------------------------
PASO 0: CONFIGURACIÓN LOCAL (¡CRUCIAL!)
------------------------------------------------------------------------------
El archivo de configuración 'env_config.sh' está ignorado por Git para proteger 
las rutas de tu propia PC. Cada miembro del equipo debe crear el suyo.

1. Crea un archivo nuevo en esta carpeta llamado: env_config.sh
2. Copia y pega el siguiente bloque dentro de ese archivo:
3. Edita las rutas para que apunten a DONDE TÚ instalaste las herramientas.

--- COPIAR DESDE AQUÍ (contenido de env_config.sh) ---

#!/bin/bash
# Define aquí dónde instalaste TUS herramientas en TU computadora.

# Ruta a la carpeta de RFdiffusion (donde clonaste el repo de Baker Lab)
export RFDIFFUSION_DIR="/home/TU_USUARIO/ruta/a/RFdiffusion"

# Ruta a la carpeta de ProteinMPNN
export MPNN_DIR="/home/TU_USUARIO/ruta/a/ProteinMPNN"

# Nombre de tu entorno de Conda (usualmente SE3nv)
export CONDA_ENV_NAME="SE3nv"

--- HASTA AQUÍ ---

------------------------------------------------------------------------------
PASO 1: GENERACIÓN DE ESTRUCTURAS (RFdiffusion)
------------------------------------------------------------------------------
* Script: run_01_rfdiffusion.sh
* Función: Genera esqueletos (backbones) que encajan geométricamente en PD-1.
* Input: data/processed_pdbs/pd1_only.pdb
* Output: outputs/01_rfdiffusion/
* Uso:
    ./scripts/run_01_rfdiffusion.sh

------------------------------------------------------------------------------
PASO 2: DISEÑO DE SECUENCIA (ProteinMPNN)
------------------------------------------------------------------------------
* Script: run_02_mpnn.sh
* Función: Asigna aminoácidos a los esqueletos del Paso 1 sin modificar PD-1.
* Input: Carpeta generada en el Paso 1.
* Output: outputs/02_proteinmpnn/ (Archivos .fasta)
* Uso:
    ./scripts/run_02_mpnn.sh

------------------------------------------------------------------------------
PASO 3: PREPARACIÓN PARA ALPHAFOLD 3
------------------------------------------------------------------------------
* Script: prepare_af3_json.py
* Función: Convierte los FASTAs en un JSON compatible con AlphaFold Server.
* Output: outputs/03_alphafold_inputs/jobs.json
* Uso:
    python scripts/prepare_af3_json.py

------------------------------------------------------------------------------
NOTAS DE SOLUCIÓN DE PROBLEMAS
------------------------------------------------------------------------------
1. Si dice "Permission denied": Ejecuta `chmod +x scripts/*.sh`
2. Si dice "Conda command not found": Asegúrate de haber iniciado conda 
   antes de correr el script o revisa que la detección automática en el script 
   coincida con tu instalación.
