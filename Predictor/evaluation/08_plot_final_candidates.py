import pandas as pd
import matplotlib.pyplot as plt
import os

file_path = "outputs/alphafold_candidates.csv"
plots_dir = "outputs/plots"

os.makedirs(plots_dir, exist_ok=True)

df = pd.read_csv(file_path)

print("Candidatos:", df.shape)

plt.figure(figsize=(8,7))

plt.scatter(
    df["PTM_pred"],
    df["IPTM_pred"],
    color="red",
    alpha=0.8
)

plt.xlabel("Predicted PTM")
plt.ylabel("Predicted IPTM")

plt.title("Selected AlphaFold Candidates")

plt.grid(True)

save_path = f"{plots_dir}/alphafold_final_candidates.png"

plt.savefig(save_path, dpi=300)
plt.close()

print("Gráfico guardado:", save_path)