# AlphaFold3 (AF3) setup + troubleshooting log (Ubuntu / Linux)

Este documento describe **paso a paso** todo el proceso para instalar y ejecutar AlphaFold3 en Linux, incluyendo los errores encontrados durante la instalación, su causa y cómo se resolvieron.

## Contexto del proyecto

- Repo principal: /home/luis-garcia/Documents/proyectos/drug-accelerator/pd-l1-drug-accelerator
- Código AlphaFold3: /home/luis-garcia/Documents/proyectos/drug-accelerator/alphafold3
- Virtualenv: /home/luis-garcia/Documents/proyectos/drug-accelerator/.venv
- Parámetros del modelo: /home/luis-garcia/Documents/proyectos/drug-accelerator/alphafold3/params

---

## 1. Error inicial: No module named 'absl'

**Causa**  
AlphaFold3 usa la librería Abseil de Google (`absl-py`) y no estaba instalada.

**Solución**

```
pip install absl-py
```

---

## 2. Error: No module named 'alphafold3'

**Causa**  
El paquete no estaba instalado como módulo Python.

**Solución**

```
pip install -e alphafold3/
```

---

## 3. Error al instalar AF3: falta ZLIB

**Causa**  
Faltaban dependencias nativas del sistema.

**Solución**

```
sudo apt install -y zlib1g-dev build-essential cmake ninja-build libboost-all-dev
```

---

## 4. Error: faltan archivos de chemistry / CCD

AlphaFold3 requiere artefactos del Chemical Component Dictionary (CCD):

- ccd.pickle
- chemical_component_sets.pickle

Estos no vienen generados por defecto.

---

## 5. Generación de ccd.pickle

Debemos estar en alphafold3/src/alphafold3/constants/converters para descargar ahi el CCD
Descargar el CCD:

```
wget https://files.wwpdb.org/pub/pdb/data/monomers/components.cif.gz
gunzip components.cif.gz
```

Generar pickle:

```
python ccd_pickle_gen.py components.cif ccd.pickle
```

---

## 6. Generación de chemical_component_sets.pickle

```
python chemical_component_sets_gen.py chemical_component_sets.pickle
```

---

---

## 7. Generación la BD de MSA/templates



---

## 7. Error de flags: model_params_dir

**Causa**  
El script usa `--model_dir`, no `--model_params_dir`.

**Solución**
Cambiar el flag en el código que construye el comando.

---

## 8. Error CUDA en VirtualBox

**Causa**
VirtualBox no soporta CUDA passthrough.

**Solución**
Migrar a:

- WSL2 + Ubuntu + NVIDIA CUDA
- Linux nativo
- Servidor/cloud con GPU

---

## 9. Recomendación final

Para Windows + GPU NVIDIA:
**WSL2 + Ubuntu** es la opción recomendada y soportada.

Verificación:

```
nvidia-smi
python -c "import jax; print(jax.devices())"
```

---

## Resumen

- absl → `pip install absl-py`
- alphafold3 → `pip install -e .`
- ZLIB → `apt install zlib1g-dev`
- CCD → generar pickles
- CUDA → no usar VirtualBox, usar WSL2
