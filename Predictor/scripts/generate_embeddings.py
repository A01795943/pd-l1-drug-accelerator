import os
import torch
import pandas as pd
import sys

# Asegurar que el script puede importar el embedder desde la carpeta models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.esm2_embedder import ESM2Embedder

def main():
    print("\n" + "="*40)
    print("🧬 STEP 2: GENERATING EMBEDDINGS (ESM-2)")
    print("="*40)

    # 1. Configuración de rutas
    input_csv = "data/processed_dataset.csv"
    output_path = "outputs/embeddings.pt"
    os.makedirs("outputs", exist_ok=True)

    if not os.path.exists(input_csv):
        print(f"❌ Error: No se encontró el archivo {input_csv}")
        return

    # 2. Cargar Dataset
    df = pd.read_csv(input_csv)
    sequences = df["seq"].astype(str).tolist()
    print(f"✅ Dataset cargado: {len(sequences)} secuencias encontradas.")

    # 3. Detectar Dispositivo (GPU/CPU)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🚀 Usando dispositivo: {device}")

    # 4. Inicializar Embedder
    # Usamos el modelo de 35M parámetros por eficiencia, puedes cambiarlo si necesitas uno más grande.
    try:
        embedder = ESM2Embedder(
            model_name="esm2_t12_35M_UR50D", 
            device=device, 
            batch_size=16  # Ajusta según la memoria de tu GPU
        )

        print("🧠 Generando embeddings... esto puede tardar unos minutos.")
        embeddings = embedder.embed(sequences)

        # 5. Guardar Tensores
        torch.save(embeddings, output_path)
        print(f"\n✅ Proceso completado exitosamente.")
        print(f"💾 Embeddings guardados en: {output_path}")
        print(f"📊 Dimensiones finales: {embeddings.shape}")

    except Exception as e:
        print(f"❌ Error durante la generación: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()