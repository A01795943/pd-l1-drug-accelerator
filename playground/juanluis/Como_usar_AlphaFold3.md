# Cómo usar AlphaFold 3 para el diseño y evaluación de proteínas

## 1. Introducción

AlphaFold 3 es un modelo de inteligencia artificial desarrollado por DeepMind que permite predecir estructuras tridimensionales de biomoléculas con alta precisión. A diferencia de versiones anteriores, AlphaFold 3 amplía su alcance para modelar no solo proteínas monoméricas, sino también complejos biomoleculares, incluyendo interacciones proteína–proteína, proteína–péptido y proteína–ligando.

En el contexto del diseño racional de proteínas y del descubrimiento acelerado de fármacos, AlphaFold 3 puede utilizarse como una herramienta de evaluación estructural temprana para validar secuencias de aminoácidos generadas por modelos de diseño como ProteinMPNN.

AlphaFold 3 recibe como parámetro principal secuencias de aminoácidos, usualmente en formato FASTA, y produce estructuras tridimensionales junto con métricas de confianza que permiten evaluar el plegamiento y las interacciones moleculares.

---

## 2. Formato FASTA y su uso en diseño de proteínas

### 2.1 ¿Qué es un archivo FASTA?

Un archivo FASTA es un formato de texto plano utilizado para almacenar secuencias biológicas. Cada secuencia contiene:

- Un encabezado que comienza con el carácter `>`
- Una secuencia de letras que representan aminoácidos

Un mismo archivo FASTA puede contener múltiples secuencias.

---

### 2.2 Ejemplo de un archivo FASTA generado por ProteinMPNN

```
>rfdiffusion_1769488951, score=2.0692, global_score=2.0692, designed_chains=['A'], seed=23
AFTVTVPKDLYVVEYGSNMTIECKFPVEKQLDLAALIVYWEMEDKNIIQFVHGEEDLKVQHSSYRQRARLLKDQLSLGNAALQITDVKLQDAGVYRCMISYGGADYKRITVKVNAPYGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG
>T=0.1, sample=1, score=0.9703, global_score=0.9703, seq_recovery=0.3333
PFKVTSPSKTYTVELGSTVSLSCNFPVEGELDLSKLTVVWEKFGQLIIEYVKGEFDPSKVDPKFQGRAYLDLESLKKGTATLVIKNVQVEDAGTYTCTITYEGTDSVDILLIVEEKTSPKKRKLYVNVLDEEKGGEIVLKEEEVELK
```

---

### 2.3 Métricas del FASTA

- **Score / global_score**: compatibilidad secuencia–estructura. Valores más bajos son mejores.
- **Temperatura (T)**: controla diversidad del muestreo. Valores bajos producen secuencias conservadoras.
- **Seq_recovery**: fracción de identidad respecto a una referencia.

---

## 3. Jobs y Entities en AlphaFold 3

### 3.1 Job

Un job es una ejecución completa e independiente de AlphaFold 3. Cada job produce una predicción estructural y métricas asociadas.

### 3.2 Entity

Una entity representa una biomolécula individual dentro de un job (proteína, péptido, ADN, etc.).

**Regla clave**:
- Alternativas de secuencia → jobs separados
- Componentes de un sistema → entities en un mismo job

---

## 4. Evaluación estructural de secuencias diseñadas

### 4.1 Selección de secuencias top N

Se seleccionan las mejores secuencias del FASTA utilizando el score más bajo de ProteinMPNN.

---

### 4.2 Evaluación de plegamiento (1 job, 1 entity)

Métricas evaluadas:

- **pLDDT (0–100)**  
  Confianza local por residuo. >90 indica alta confiabilidad.

- **pTM (0–1)**  
  Confianza en la topología global. >0.7 indica plegamiento confiable.

Solo secuencias con pLDDT y pTM altos avanzan.

---

## 5. Evaluación de interacción con PD-L1

### 5.1 Configuración

- 1 job
- 2 entities:
  - Secuencia diseñada
  - PD-L1

---

### 5.2 Métricas de interacción

- **ipTM (0–1)**  
  Confianza en la interfaz entre cadenas. >0.6 es deseable.

- **PAE inter-cadenas**  
  Valores bajos en la interfaz indican interacción estable.

---

## 6. Péptidos vs proteínas

### Péptido
- <50 aminoácidos
- Alta flexibilidad
- Menor estabilidad

### Proteína o mini-proteína
- >50 aminoácidos
- Estructura definida
- Mayor estabilidad y afinidad

---

## 7. Conclusión

AlphaFold 3 permite filtrar y priorizar secuencias diseñadas computacionalmente antes de análisis más costosos, siempre que sus métricas se interpreten correctamente.

---

## 8. Referencias

DeepMind. (2024). Accurate structure prediction of biomolecular interactions with AlphaFold 3. *Nature*. https://www.nature.com/articles/s41586-024-07487-w

Dauparas, J., et al. (2022). Robust deep learning–based protein sequence design using ProteinMPNN. *Science*, 378(6615), 49–56.
