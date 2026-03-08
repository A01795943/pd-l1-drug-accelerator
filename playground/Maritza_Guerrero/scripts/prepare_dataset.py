# Validador/scripts/prepare_dataset.py

import pandas as pd

# Cargar dataset original
df = pd.read_csv("data/Estructuras2.csv")

# Seleccionar solo las columnas necesarias
df_new = df[['seq','ptm','i_ptm']].copy()

# Guardar nuevo dataset procesado
df_new.to_csv("../data/processed_dataset.csv", index=False)

print("Processed dataset saved at ../data/processed_dataset.csv")