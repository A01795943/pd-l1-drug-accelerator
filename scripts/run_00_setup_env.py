import os
import sys
import subprocess
import platform

# =============================================================================
# 🛠️ SETUP MAESTRO: PREPARACIÓN DEL ENTORNO DE TRABAJO
# =============================================================================

def print_header(text):
    print("\n" + "=" * 60)
    print(f"🔧 {text}")
    print("=" * 60)

def check_python_version():
    print_header("1. Verificando Python")
    v = sys.version_info
    print(f"   -> Python detectado: {v.major}.{v.minor}.{v.micro}")
    if v.major < 3 or (v.major == 3 and v.minor < 8):
        print("   ❌ ERROR: Se requiere Python 3.8 o superior.")
        sys.exit(1)
    print("   ✅ Versión correcta.")

def create_directory_structure(root_path):
    print_header("2. Creando Estructura de Carpetas")
    
    folders = [
        "data/references",
        "data/raw",
        "outputs/01_diffusion",
        "outputs/02_proteinmpnn",
        "outputs/03_alphafold_inputs",
        "scripts",
        "notebooks"
    ]

    for folder in folders:
        full_path = os.path.join(root_path, folder)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
            print(f"   📂 Creado: {folder}/")
        else:
            print(f"   ✅ Existe: {folder}/")

def check_and_install_requirements():
    print_header("3. Verificando Librerías Necesarias")
    
    required = ["pandas", "requests", "python-dotenv", "biopython"]
    missing = []

    for lib in required:
        try:
            __import__(lib)
            print(f"   ✅ Instalado: {lib}")
        except ImportError:
            # Casos especiales de nombres de importación
            if lib == "python-dotenv":
                try: __import__("dotenv"); print(f"   ✅ Instalado: {lib}"); continue
                except: pass
            if lib == "biopython":
                try: __import__("Bio"); print(f"   ✅ Instalado: {lib}"); continue
                except: pass
            
            print(f"   ❌ Falta: {lib}")
            missing.append(lib)

    if missing:
        print(f"\n   ⚠️  Faltan {len(missing)} librerías. ¿Deseas instalarlas ahora? (y/n)")
        choice = input("   > ").lower()
        if choice == 'y':
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
            print("\n   ✅ Instalación completada.")
        else:
            print("   ⚠️  Recuerda instalarlas manualmente con 'pip install ...'")

def setup_env_file(root_path):
    print_header("4. Configurando Secretos (.env)")
    
    env_path = os.path.join(root_path, ".env")
    
    if os.path.exists(env_path):
        print("   ✅ El archivo .env ya existe. No se modificará.")
        return

    print("   ⚠️  No se encontró archivo .env. Vamos a crearlo.")
    print("   (Presiona Enter para dejar en blanco y rellenar luego)")
    
    nvidia_key = input("\n   🔑 Pega tu NVIDIA API KEY (nvapi-...): ").strip()
    mpnn_path = input("   🧬 Ruta local de ProteinMPNN: ").strip()

    env_content = f"""# VARIABLES DE ENTORNO DEL PROYECTO
# Generado automáticamente por run_00_setup_env.py

# API Key para RFdiffusion (NVIDIA NIM)
NVIDIA_API_KEY={nvidia_key}

# Ruta local de ProteinMPNN
MPNN_PATH={mpnn_path}
"""
    
    with open(env_path, "w") as f:
        f.write(env_content)
    
    print(f"\n   ✅ Archivo creado en: {env_path}")
    print("   (Recuerda que este archivo NO se debe subir a GitHub)")

def check_target_pdb(root_path):
    print_header("5. Verificando Archivo Target (PD-L1)")
    target_path = os.path.join(root_path, "data", "references", "target_alphafold.pdb")
    
    if os.path.exists(target_path):
        print("   ✅ PDB de referencia encontrado.")
    else:
        print("   ⚠️  No existe 'target_alphafold.pdb' en data/references/")
        print("      Por favor, coloca tu archivo PDB limpio ahí para que funcione el Paso 1.")

def main():
    # Obtener la raíz del proyecto (asumiendo que este script está en /scripts)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    print(f"🏠 Raíz del proyecto detectada: {project_root}")
    
    check_python_version()
    create_directory_structure(project_root)
    check_and_install_requirements()
    setup_env_file(project_root)
    check_target_pdb(project_root)
    
    print_header("¡SETUP COMPLETADO!")
    print("   🚀 Tu entorno está listo.")
    print("   Pasos siguientes:")
    print("   1. Coloca tu PDB en 'data/references/target_alphafold.pdb'")
    print("   2. Ejecuta 'python scripts/run_01_nvidia_api.py'")

if __name__ == "__main__":
    main()