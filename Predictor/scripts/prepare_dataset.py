# Validador/scripts/prepare_dataset.py
import pandas as pd
import os

print("Loading original dataset...")

df = pd.read_csv("data/Estructuras2.csv")

df = df.rename(columns={
    "mpnn": "score",
    "ptm": "PTM",
    "i_ptm": "IPTM"
})

df = df[["seq", "score", "PTM", "IPTM"]]

os.makedirs("data", exist_ok=True)

df.to_csv("data/processed_dataset.csv", index=False)

print("Processed dataset saved")
print(df.head())
print("Shape:", df.shape)