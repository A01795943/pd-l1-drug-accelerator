# evaluation/05_evaluate_model.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import r2_score, mean_squared_error
from scipy.stats import spearmanr
import os

# -----------------------------
# Paths
# -----------------------------
real_file = "../data/processed_dataset.csv"
pred_file = "../outputs/predictions_all_models.csv"
candidates_file = "../outputs/alphafold_candidates.csv"

os.makedirs("../outputs/plots", exist_ok=True)

# -----------------------------
# Load data
# -----------------------------
df_real = pd.read_csv(real_file)
df_pred = pd.read_csv(pred_file)

# -----------------------------
# Targets y modelos
# -----------------------------
targets = ["PTM","IPTM"]
models = ["ridge","rf","mlp","xgb","lgb"]

results = []

# -----------------------------
# Evaluación principal
# -----------------------------
for model in models:

    for target in targets:

        pred_col = f"{model}_{target}"

        if pred_col not in df_pred.columns:
            continue

        y_true = df_pred[f"{target}_real"]
        y_pred = df_pred[pred_col]

        r2 = r2_score(y_true, y_pred)
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        sp = spearmanr(y_true, y_pred).correlation

        results.append({
            "model":model,
            "target":target,
            "R2":r2,
            "MSE":mse,
            "RMSE":rmse,
            "Spearman":sp
        })

        print(f"\n{model} {target}")
        print("R2:",round(r2,4))
        print("RMSE:",round(rmse,4))
        print("Spearman:",round(sp,4))

        # -----------------------------
        # Scatter Real vs Pred
        # -----------------------------
        plt.figure(figsize=(6,6))

        sns.regplot(
            x=y_true,
            y=y_pred,
            scatter_kws={"alpha":0.5},
            line_kws={"color":"blue"}
        )

        plt.plot([0,1],[0,1],'r--',label="Ideal")

        plt.xlabel("Real")
        plt.ylabel("Predicted")

        plt.title(f"{model} {target}")

        plt.legend()

        plt.savefig(f"../outputs/plots/{model}_{target}_scatter.png")

        plt.close()

        # -----------------------------
        # Error distribution
        # -----------------------------
        error = y_true - y_pred

        plt.figure(figsize=(6,4))

        sns.histplot(error,bins=40)

        plt.title(f"Error distribution {model} {target}")

        plt.savefig(f"../outputs/plots/{model}_{target}_error_hist.png")

        plt.close()

# -----------------------------
# Guardar métricas
# -----------------------------
df_results = pd.DataFrame(results)

df_results.to_csv("../outputs/model_metrics.csv",index=False)

print("\nMetrics saved to outputs/model_metrics.csv")

# -----------------------------
# Comparación de modelos
# -----------------------------
plt.figure(figsize=(8,5))
sns.barplot(data=df_results,x="model",y="R2",hue="target")
plt.title("R2 comparison")
plt.savefig("../outputs/plots/model_R2_comparison.png")
plt.close()

plt.figure(figsize=(8,5))
sns.barplot(data=df_results,x="model",y="RMSE",hue="target")
plt.title("RMSE comparison")
plt.savefig("../outputs/plots/model_RMSE_comparison.png")
plt.close()

plt.figure(figsize=(8,5))
sns.barplot(data=df_results,x="model",y="Spearman",hue="target")
plt.title("Spearman comparison")
plt.savefig("../outputs/plots/model_spearman_comparison.png")
plt.close()

# -----------------------------
# Dataset analysis
# -----------------------------
df = pd.read_csv(real_file)

plt.figure(figsize=(6,6))
plt.scatter(df["score"],df["PTM"],alpha=0.5)
plt.xlabel("MPNN score")
plt.ylabel("PTM")
plt.title("MPNN vs PTM")
plt.savefig("../outputs/plots/mpnn_vs_ptm.png")
plt.close()

plt.figure(figsize=(6,6))
plt.scatter(df["score"],df["IPTM"],alpha=0.5)
plt.xlabel("MPNN score")
plt.ylabel("IPTM")
plt.title("MPNN vs IPTM")
plt.savefig("../outputs/plots/mpnn_vs_iptm.png")
plt.close()

print("\nDataset analysis plots saved.")

# =====================================================
# Evaluación de candidatos seleccionados
# =====================================================

if os.path.exists(candidates_file):

    df_candidates = pd.read_csv(candidates_file)

    print("\nCandidatos cargados:", df_candidates.shape)

    # -----------------------------
    # Scatter con regresión
    # -----------------------------
    for model in models:

        for target in targets:

            pred_col = f"{model}_{target}"

            if pred_col not in df_candidates.columns:
                continue

            y_true = df_candidates[f"{target}_real"]
            y_pred = df_candidates[pred_col]

            plt.figure(figsize=(6,6))

            sns.regplot(
                x=y_true,
                y=y_pred,
                scatter_kws={"alpha":0.6},
                line_kws={"color":"blue"}
            )

            plt.plot([0,1],[0,1],'r--',label="Ideal")

            plt.xlabel("Real")
            plt.ylabel("Predicted")

            plt.title(f"Candidatos {model} {target}")

            plt.legend()

            plt.savefig(
                f"../outputs/plots/candidates_{model}_{target}_regression.png"
            )

            plt.close()

    # -----------------------------
    # Comparación entre modelos
    # -----------------------------
    colors = {
        "ridge":"blue",
        "rf":"green",
        "mlp":"orange",
        "xgb":"purple",
        "lgb":"brown"
    }

    plt.figure(figsize=(8,6))

    for model in models:

        pred_col = f"{model}_PTM"

        if pred_col not in df_candidates.columns:
            continue

        plt.scatter(
            df_candidates["PTM_real"],
            df_candidates[pred_col],
            alpha=0.6,
            color=colors.get(model,"gray"),
            label=model
        )

    plt.plot([0,1],[0,1],'k--',label="Ideal")

    plt.xlabel("PTM real")
    plt.ylabel("PTM predicho")

    plt.title("Comparación de modelos (candidatos)")

    plt.legend()
    plt.grid(True)

    plt.savefig("../outputs/plots/candidates_model_comparison.png")

    plt.close()

    print("\nCandidate evaluation plots generated.")

else:

    print("\nNo candidate file found. Skipping candidate evaluation.")

print("\nAll plots saved in outputs/plots/")