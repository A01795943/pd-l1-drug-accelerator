# Generación de Agonistas de PD-L1 usando RF Diffusion, Protein MPNN y AlphaFold3

## Objetivo
Generar nuevos péptidos/proteínas agonistas de PD-L1 (Programmed Death-Ligand 1) para el tratamiento de cáncer mediante inmunoterapia.

## Contexto Biológico

**PD-L1** es una proteína de superficie celular que interactúa con PD-1 en células T, suprimiendo la respuesta inmunitaria. Los agonistas de PD-L1 pueden:
- Potenciar la respuesta inmunitaria contra células cancerosas
- Mejorar la eficacia de la inmunoterapia
- Reducir la resistencia a tratamientos actuales

## Pipeline Propuesto

```
1. RF Diffusion
   ↓ Genera estructuras de proteínas candidatas
   
2. Protein MPNN
   ↓ Diseña secuencias que se plieguen a las estructuras
   
3. AlphaFold3
   ↓ Valida que las secuencias se plieguen correctamente
   
4. Evaluación y Filtrado
   ↓ Predicción de afinidad, propiedades farmacológicas
```

## Herramientas y APIs

### RF Diffusion
- **API**: NVIDIA NIM RFdiffusion
- **Endpoint**: `https://health.api.nvidia.com/v1/biology/ipd/rfdiffusion/generate`
- **Uso**: Generación de estructuras proteicas de novo

### Protein MPNN
- **Instalación**: `pip install protein-mpnn-pip` o Docker
- **Uso**: Diseño de secuencias para estructuras dadas
- **Input**: Archivos PDB
- **Output**: Secuencias de aminoácidos

### AlphaFold3
- **Instalación**: GitHub de Google DeepMind (requiere acceso a parámetros)
- **Uso**: Predicción de estructuras 3D
- **Input**: Secuencias de aminoácidos
- **Output**: Estructuras PDB predichas

## Notas Importantes

1. **AlphaFold3** requiere solicitar acceso a Google DeepMind para obtener los parámetros del modelo (~250 GB)
2. **RF Diffusion** requiere API key de NVIDIA Build
3. **Protein MPNN** puede ejecutarse localmente o vía API
