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

### 5.3 Secuencia FASTA de PD-L1

```
>sp|Q9NZQ7|PD1L1_HUMAN Programmed cell death 1 ligand 1 OS=Homo sapiens OX=9606 GN=CD274 PE=1 SV=1
MDSKGNKLLSVLLLWVLLLWASPMAEVQPTLTVPLTVLHDGKGQGSVVLHNHAPIQSGVTFHEGIIPS
SFHGELKRVTLGPLPSLFITLDKDLQGAGAFGPGGATYEKVTLYFQSQLVGGSEVGLEYRKHCFMEG
PIHGPSNVVLTSLTIPYSASHLGGGTHVKNQVQTAVSFTIPCVRHCGTSSCVNGGGGTVTIKTVECT
AQGPNHSVITLKVLGTYGPVVQDRVVWQGLYNYGEKDIQHPSMDFGAYSLTHKLPQVRDSRGYRFIP
VQSEENRLIVHSVNPQLWYSLKKLTPIQGLDNLPSDFQEHREGDTRHYEELSVFPDGGGIYTIKPCL
FPRGGLWDVCAKPLASESWLGNVDSGLKEQTLSVGDSKTQSLSAATRVQWGDVVIGEVTVTVSPSSS
SSESQKSLSEKLETQTWSSYRGDPSSVCTGPGEGKTATNNDYLVGTTLGMSSSSSSLPLPSRHSRAPS
PSRPGSLEAATA

>PD-L1_human_extracellular_domain
QPTLTVPLTVLHDGKGQGSVVLHNHAPIQSGVTFHEGIIPSSFHGELKRVTLGPLPSLFITLDKDLQGAGAFGPGGATYEKVTLYFQSQLVGGSEVGLEYRKHCFMEGPIHGPSNVVLTSLTIPYSASHLGGGTHVKNQVQTAVSFTIPCVRHCGTSSCVNGGGGTVTIKTVECTAQGPNHSVITLKVLGTYGPVVQDRVVWQGLYNYGEKDIQHPSMDFGAYSLTHKLPQVRDSRGYRFIPVQSEENRLIVHSVNPQLWYSLKKLTPIQGLDNLPSDFQEHREGDTRHYEELSVFPDGGGIYTIKPCLFPRGGLWDVCAKPLASESWLGNVDSGLKEQTL

```
### 5.4 Notas sobre la secuencia FASTA de PD-L1 (CD274)

#### Información general

Esta secuencia corresponde a la **forma completa de PD-L1 humana**, codificada por el gen **CD274** y anotada en UniProt con el identificador **Q9NZQ7**.  
PD-L1 (*Programmed cell death 1 ligand 1*) es una proteína clave en la regulación de la respuesta inmune y un objetivo central en inmunoterapia contra el cáncer.

🔗 **Referencia UniProt:**  
https://www.uniprot.org/uniprotkb/Q9NZQ7/entry

---

#### Tipo de proteína

PD-L1 es una **proteína transmembrana tipo I**, lo que implica que:

- Posee un **dominio extracelular N-terminal**
- Contiene **una sola hélice transmembrana**
- Presenta una **cola citosólica C-terminal corta**

El dominio extracelular es el responsable directo de la **interacción con el receptor PD-1** en las células T.

🔗 **Información general sobre PD-L1:**  
https://en.wikipedia.org/wiki/PD-L1

---

#### Componentes estructurales de la secuencia

La secuencia FASTA completa incluye las siguientes regiones funcionales:

##### 1. Péptido señal (Signal peptide)
Ubicado al inicio de la secuencia, permite la correcta inserción y direccionamiento de la proteína hacia la vía secretora y la membrana celular.

### 2. Dominio extracelular
Región responsable de la interacción con **PD-1**.  
Este dominio es el principal objetivo en estudios de:
- diseño de agonistas o antagonistas,
- docking proteína–proteína,
- diseño de péptidos o mini-proteínas terapéuticas.

##### 3. Región transmembrana y cola citosólica
La secuencia incluye la región transmembrana, pero **termina antes de una cola citosólica larga**, lo cual es común en anotaciones enfocadas al dominio funcional principal.

---

#### Longitud de la secuencia

- **Longitud total:** 290 aminoácidos  
- **Especie:** *Homo sapiens*

Esta longitud corresponde a la isoforma canónica reportada en UniProt.

---

#### Uso en modelado estructural

Para estudios computacionales (por ejemplo, AlphaFold, docking o diseño de proteínas):

- Es común utilizar **solo el dominio extracelular**, excluyendo:
  - el péptido señal
  - la región transmembrana
- Esto facilita el modelado y evita artefactos estructurales relacionados con la membrana.

---

#### Referencias

- UniProt Consortium. *CD274 – Programmed cell death 1 ligand 1*.  
  https://www.uniprot.org/uniprotkb/Q9NZQ7/entry

- Wikipedia contributors. *PD-L1*.  
  https://en.wikipedia.org/wiki/PD-L1
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
