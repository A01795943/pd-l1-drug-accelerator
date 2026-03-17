import lightgbm as lgb
from sklearn.multioutput import MultiOutputRegressor
import joblib
import os

class LightGBMModel:
    def __init__(self):
        # Ajuste de hiperparámetros para balancear velocidad y precisión
        base = lgb.LGBMRegressor(
            n_estimators=500,
            learning_rate=0.03,
            max_depth=8,
            subsample=0.9,
            colsample_bytree=0.8,
            random_state=42,
            verbosity=-1  # Menos ruido en consola
        )
        self.model = MultiOutputRegressor(base)

    def fit(self, X, y):
        print("Training LightGBM model...")
        self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X)

    def save(self, path):
        # Crear carpeta si no existe antes de guardar
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self.model, path)
        print(f"LightGBM model saved to {path}")