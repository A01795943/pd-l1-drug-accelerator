import os
import requests
import json
import urllib.request
import time
from dotenv import load_dotenv
from datetime import datetime

# ==============================================================================
# 🔑 CONFIGURACIÓN & API
# ==============================================================================

# Cargar variables de entorno (Con comillas para evitar errores)
load_dotenv("api.env") 
API_KEY = os.getenv("NVIDIA_API_KEY")

if not API_KEY:
    raise ValueError("❌ ERROR: No se encontró la NVIDIA_API_KEY. Revisa tu archivo api.env")

# ==============================================================================
# ⚙️ CONFIGURACIÓN DEL PROYECTO
# ==============================================================================

# Rutas dinámicas
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# Carpeta de salida
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "outputs", "01_diffusion")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Archivo de entrada (Target)
INPUT_PDB_PATH = os.path.join(PROJECT_ROOT, "data", "references", "target_alphafold.pdb")
os.makedirs(os.path.dirname(INPUT_PDB_PATH), exist_ok=True)

# URL DE LA API (RFdiffusion)
INVOKE_URL = "https://health.api.nvidia.com/v1/biology/ipd/rfdiffusion/generate"
# Nota: Si esta URL falla, intenta con la de /ipd/ que tenías antes, pero NVIDIA suele unificarlas.
# Tambien verifica la URL para ver que este funcionando perfectamente dentro del codigo pueden cambiar muchas veces

# ==============================================================================
# 📥 FUNCIONES
# ==============================================================================

def force_download_pdb_from_alphafold():
    """Descarga el PDB fresco desde la base de datos de AlphaFold (Tu lógica original)."""
    if os.path.exists(INPUT_PDB_PATH):
        print("✅ El archivo PDB ya existe. Usando versión local.")
        return True

    print("⬇️  Descargando PDB fresco de AlphaFold (Q9NZQ7)...")
    try:
        # Tu lógica original para obtener la URL
        url_api = 'https://alphafold.ebi.ac.uk/api/prediction/Q9NZQ7'
        with urllib.request.urlopen(url_api) as r:
            data = json.load(r)
            pdb_url = data[0]['pdbUrl']
        
        # Descargar contenido
        pdb_content = requests.get(pdb_url).text
        
        # Limpieza (Solo líneas ATOM para evitar basura que confunda a la IA)
        lines = pdb_content.split('\n')
        atom_lines = [line for line in lines if line.startswith("ATOM")]
        clean_content = "\n".join(atom_lines)
        
        with open(INPUT_PDB_PATH, "w") as f:
            f.write(clean_content)
            
        print(f"✅ PDB Descargado y Limpio ({len(clean_content)} bytes).")
        return True
    except Exception as e:
        print(f"❌ Error crítico al descargar: {e}")
        return False

def run_production_batch():
    # 1. Asegurar que tenemos el target
    if not force_download_pdb_from_alphafold():
        return

    # 2. Leer el PDB para enviarlo
    with open(INPUT_PDB_PATH, "r") as f: 
        pdb_content = f.read()

    # 3. Configuración de la corrida masiva
    TOTAL_DESIGNS = 40  # <--- AQUÍ ESTÁ EL CAMBIO PARA HACER 40
    TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M')
    
    print("-" * 60)
    print(f"🚀 Iniciando producción masiva: {TOTAL_DESIGNS} estructuras...")
    print(f"🎯 Target: PD-L1 (AlphaFold Q9NZQ7) | Residuos 1-120")
    print(f"🧬 Binder: 70 aminoácidos de largo")
    print("-" * 60)

    success_count = 0
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # BUCLE DE 40 DISEÑOS
    for i in range(1, TOTAL_DESIGNS + 1):
        try:
            design_id = f"design_{TIMESTAMP}_{i:02d}"
            
            # TU PAYLOAD ORIGINAL (CON AJUSTE DE SINTAXIS)
            # Usamos espacios en lugar de comas para evitar el error 422
            # "A1-120": Tu rango original
            # "0": Separador (corte)
            # "70-70": Tu longitud de binder original
            payload = {
                "input_pdb": pdb_content,
                "contigs": "A1-120 0 70-70" 
            }
            
            print(f"⏳ [{i}/{TOTAL_DESIGNS}] Generando {design_id}...")
            
            response = requests.post(INVOKE_URL, headers=headers, json=payload, timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                # Buscar la respuesta en cualquiera de los formatos posibles
                pdb_data = data.get("pdb") or data.get("protein") or data.get("output_pdb")
                
                if pdb_data:
                    out_path = os.path.join(OUTPUT_DIR, f"{design_id}.pdb")
                    with open(out_path, "w") as f:
                        f.write(pdb_data)
                    print(f"   ✅ Guardado.")
                    success_count += 1
                else:
                    print(f"   ⚠️ API respondió ok, pero sin PDB.")
            
            elif response.status_code == 429:
                print("   🚨 Muy rápido. Pausando 10 segundos...")
                time.sleep(10)
            else:
                print(f"   ❌ Error {response.status_code}: {response.text}")
            
            # Pequeña pausa para no saturar
            time.sleep(1.5)

        except Exception as e:
            print(f"   🔥 Error de script: {e}")

    print("-" * 60)
    print(f"🏁 Finalizado. {success_count}/{TOTAL_DESIGNS} diseños exitosos.")

if __name__ == "__main__":
    run_production_batch()