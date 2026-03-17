import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_final_candidates():
    file_path = "outputs/alphafold_candidates.csv"
    plots_dir = "outputs/plots"
    os.makedirs(plots_dir, exist_ok=True)

    if not os.path.exists(file_path):
        print(f"❌ No se encontró {file_path}")
        return

    df = pd.read_csv(file_path)
    print(f"Graficando {df.shape[0]} candidatos finales...")

    plt.figure(figsize=(8, 7))
    plt.scatter(
        df["PTM_pred"],
        df["IPTM_pred"],
        color="crimson",
        alpha=0.7,
        edgecolors='white',
        linewidth=0.5
    )

    plt.xlabel("Predicted PTM")
    plt.ylabel("Predicted IPTM")
    plt.title("Selected AlphaFold Candidates (Final Set)")
    plt.xlim(0.65, 1.0) # Zoom en la zona de interés
    plt.ylim(0.65, 1.0)
    plt.grid(True, linestyle=':', alpha=0.6)

    save_path = os.path.join(plots_dir, "alphafold_final_candidates.png")
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Gráfico guardado: {save_path}")

if __name__ == "__main__":
    plot_final_candidates()