import shutil
import os

def clean_outputs():
    path = "outputs"
    if os.path.exists(path):
        print(f"Cleaning {path} directory...")
        shutil.rmtree(path)
    
    # Recrear la estructura base necesaria
    os.makedirs("outputs/models", exist_ok=True)
    os.makedirs("outputs/plots", exist_ok=True)
    
    # Crear placeholders para evitar errores de "File Not Found" en otros scripts
    print("Outputs directory structure recreated.")

if __name__ == "__main__":
    clean_outputs()
    print("Clean-up complete.")