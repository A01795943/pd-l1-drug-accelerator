import os
import requests
import json
import urllib.request
import time
from dotenv import load_dotenv
from datetime import datetime

# ==============================================================================
# 🔑 CONFIGURACIÓN: Configuracion de la API aqui tienes que crear en la raiz el archivo de lectura de tu API
# ==============================================================================

load_dotenv(api.env)
API_KEY = os.getenv(NVIDIA_API_KEY) 
# ==============================================================================

# --- RUTAS DINÁMICAS ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

# Creamos un ID único basado en el momento exacto de la ejecución
SESSION_ID = datetime.now().strftime('%Y%m%d_%H%M%S')

# Definimos la carpeta de resultados (la que renombramos anteriormente)
OUTPUT_BASE = os.path.join(PROJECT_ROOT, "outputs", "01_rfdiffusion_results")

# El archivo ahora tendrá la fecha en el nombre para no borrarse nunca
OUTPUT_FILE = f"design_nvidia_{SESSION_ID}.pdb"
OUTPUT_DIR = os.path.join(OUTPUT_BASE, OUTPUT_FILE)

# Aseguramos que la carpeta base exista
os.makedirs(OUTPUT_BASE, exist_ok=True)

# URL CORRECTA (IPD)
INVOKE_URL = "https://health.api.nvidia.com/v1/biology/ipd/rfdiffusion/generate"

def force_download_pdb():
    """Borra el PDB anterior y descarga uno nuevo para asegurar que no esté vacío."""
    if os.path.exists(INPUT_PDB):
        os.remove(INPUT_PDB)

    print("⬇️  Descargando PDB fresco de AlphaFold...")
    try:
        url_api = 'https://alphafold.ebi.ac.uk/api/prediction/Q9NZQ7'
        with urllib.request.urlopen(url_api) as r:
            data = json.load(r)
            pdb_url = data[0]['pdbUrl']
        
        pdb_content = requests.get(pdb_url).text
        
        # Filtramos solo líneas ATOM para evitar basura
        lines = pdb_content.split('\n')
        atom_lines = [line for line in lines if line.startswith("ATOM")]
        clean_content = "\n".join(atom_lines)
        
        with open(INPUT_PDB, "w") as f:
            f.write(clean_content)
            
        print(f"✅ PDB Generado ({len(clean_content)} bytes).")
        return True
    except Exception as e:
        print(f"❌ Error crítico: {e}"); return False

def run_batch():
    if "nvapi-XXX" in API_KEY:
        print("❌ ERROR: Pega tu API KEY en la línea 9.")
        return

    if not force_download_pdb(): return

    with open(INPUT_PDB, "r") as f: 
        pdb_content = f.read()

    if len(pdb_content) < 100:
        print("❌ ERROR: PDB vacío."); return

    payload = {
        "input_pdb": pdb_content,
        "contigs": "A1-120/0 70-70" 
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    print("-" * 50)
    print(f"🚀 Conectando a NVIDIA Cloud (H100)...")
    
    try:
        response = requests.post(INVOKE_URL, headers=headers, json=payload, timeout=120)
        
        if response.status_code != 200:
            print(f"❌ Error API ({response.status_code}): {response.text}")
            return

        data = response.json()
        
        # --- AQUÍ ESTÁ LA CORRECCIÓN MÁGICA ---
        # Antes buscábamos 'pdb', ahora buscamos 'output_pdb' (que es lo que llegó)
        pdb_data = data.get("output_pdb") or data.get("pdb")
        
        if pdb_data:
            file_name = "design_nvidia_final.pdb"
            out_path = os.path.join(OUTPUT_DIR, file_name)
            with open(out_path, "w") as f:
                f.write(pdb_data)
            print(f"\n🎉 ¡VICTORIA! 🧬")
            print(f"✅ Estructura guardada en: {out_path}")
            print("👉 Abre este archivo en ChimeraX o PyMOL.")
        else:
            print(f"⚠️  Respuesta rara. Claves recibidas: {data.keys()}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_batch()
