import os
import torch
import numpy as np
import pandas as pd
import joblib
import time

from IPython.display import display

from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
from scipy.stats import spearmanr

from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.neural_network import MLPRegressor
from xgboost import XGBRegressor

from models.lightgbm_model import LightGBMModel


print("====================================")
print("PIPELINE: MODEL TRAINING")
print("====================================")

os.makedirs("outputs/models",exist_ok=True)

# -------------------------------------------------
# Cargar datos
# -------------------------------------------------

print("\nLoading dataset...")

df = pd.read_csv("data/processed_dataset.csv")
print("Dataset loaded")

display(df.head())

print("\nLoading embeddings...")
embeddings = torch.load("outputs/embeddings.pt")
print("Embeddings loaded")

scores = df["score"].values.reshape(-1,1)

X = np.concatenate([embeddings.numpy(),scores],axis=1)
y = df[["PTM","IPTM"]].values

print("\nFeature matrix shape:",X.shape)
print("Target matrix shape:",y.shape)

# -------------------------------------------------
# Train Test Split
# -------------------------------------------------

print("\nSplitting dataset...")

X_train,X_test,y_train,y_test = train_test_split(
    X,y,test_size=0.2,random_state=42
)

print("Train samples:",X_train.shape[0])
print("Test samples:",X_test.shape[0])

np.save("outputs/X_test.npy",X_test)
np.save("outputs/y_test.npy",y_test)

print("Test data saved")

# -------------------------------------------------
# Modelos
# -------------------------------------------------

models = {

"ridge": MultiOutputRegressor(Ridge()),

"rf": MultiOutputRegressor(
        RandomForestRegressor(
            n_estimators=200,
            max_depth=25,
            n_jobs=-1,
            random_state=42
        )
    ),

"xgb": MultiOutputRegressor(
        XGBRegressor(
            n_estimators=600,
            learning_rate=0.03,
            max_depth=8,
            subsample=0.9,
            colsample_bytree=0.8,
            tree_method="hist",
            objective="reg:squarederror",
            random_state=42,
            n_jobs=-1
        )
    ),

"mlp_sklearn": MultiOutputRegressor(
        MLPRegressor(
            hidden_layer_sizes=(256,128),
            max_iter=500,
            random_state=42
        )
    )
}

lightgbm = LightGBMModel()

results=[]
predictions=pd.DataFrame()

predictions["PTM_real"]=y_test[:,0]
predictions["IPTM_real"]=y_test[:,1]

# -------------------------------------------------
# Entrenamiento modelos
# -------------------------------------------------

print("\n====================================")
print("TRAINING MODELS")
print("====================================")

for name,model in models.items():

    print("\n------------------------------------")
    print("Training model:",name)
    print("------------------------------------")

    start=time.time()

    model.fit(X_train,y_train)

    elapsed=time.time()-start

    print(f"{name} training finished in {round(elapsed,2)} seconds")

    joblib.dump(model,f"outputs/models/{name}.pkl")
    print(f"{name} model saved")

    preds=model.predict(X_test)

    predictions[f"{name}_PTM"]=preds[:,0]
    predictions[f"{name}_IPTM"]=preds[:,1]

    for i,target in enumerate(["PTM","IPTM"]):

        r2=r2_score(y_test[:,i],preds[:,i])
        mse=mean_squared_error(y_test[:,i],preds[:,i])
        rmse=np.sqrt(mse)
        sp=spearmanr(y_test[:,i],preds[:,i]).correlation

        print(f"{name} -> {target} | R2={r2:.4f} RMSE={rmse:.4f} Spearman={sp:.4f}")

        results.append({
        "model":name,
        "target":target,
        "R2":r2,
        "MSE":mse,
        "RMSE":rmse,
        "Spearman":sp
        })

# -------------------------------------------------
# LightGBM
# -------------------------------------------------

print("\n====================================")
print("TRAINING LIGHTGBM")
print("====================================")

start=time.time()

lightgbm.fit(X_train,y_train)

elapsed=time.time()-start

print("LightGBM training finished in",round(elapsed,2),"seconds")

lightgbm.save("outputs/models/lightgbm.pkl")
print("LightGBM model saved")

preds=lightgbm.predict(X_test)

predictions["lgb_PTM"]=preds[:,0]
predictions["lgb_IPTM"]=preds[:,1]

for i,target in enumerate(["PTM","IPTM"]):

    r2=r2_score(y_test[:,i],preds[:,i])
    mse=mean_squared_error(y_test[:,i],preds[:,i])
    rmse=np.sqrt(mse)
    sp=spearmanr(y_test[:,i],preds[:,i]).correlation

    print(f"LightGBM -> {target} | R2={r2:.4f} RMSE={rmse:.4f} Spearman={sp:.4f}")

    results.append({
    "model":"lightgbm",
    "target":target,
    "R2":r2,
    "MSE":mse,
    "RMSE":rmse,
    "Spearman":sp
    })

# -------------------------------------------------
# Guardar resultados
# -------------------------------------------------

print("\nSaving predictions...")

predictions.to_csv("outputs/predictions_all_models.csv",index=False)

print("Predictions saved")

metrics_df = pd.DataFrame(results)

metrics_df.to_csv("outputs/model_metrics.csv",index=False)

print("Metrics saved")

print("\nMetrics preview:")
display(metrics_df.head())

print("\nPredictions preview:")
display(predictions.head())

print("\n====================================")
print("TRAINING FINISHED SUCCESSFULLY")
print("====================================")