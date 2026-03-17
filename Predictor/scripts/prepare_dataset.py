# scripts/prepare_dataset.py
import pandas as pd
import os

def prepare_data():
    input_path = "data/Estructuras3.csv"
    output_path = "data/processed_dataset.csv"

    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    print(f"Loading original dataset from {input_path}...")
    df = pd.read_csv(input_path)

    # Renombrado de columnas según tu especificación
    df = df.rename(columns={
        "mpnn": "score",
        "ptm": "PTM",
        "i_ptm": "IPTM"
    })

    # Selección de columnas de interés
    # Nota: Asegúrate de que estas columnas existan en Estructuras3.csv
    cols_to_keep = ["seq", "score", "PTM", "IPTM"]
    df = df[cols_to_keep]

    # Limpieza básica: quitar espacios en blanco en las secuencias
    df['seq'] = df['seq'].str.strip()

    # Asegurar que el directorio data existe
    os.makedirs("data", exist_ok=True)

    # Guardar el dataset procesado
    df.to_csv(output_path, index=False)

    print(f"Processed dataset saved to {output_path}")
    print("\nFirst 5 rows:")
    print(df.head())
    print(f"\nShape: {df.shape}")

if __name__ == "__main__":
    prepare_data()