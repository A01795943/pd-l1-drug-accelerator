from sklearn.ensemble import RandomForestRegressor
import joblib
import time
import os

class RandomForestModel:
    def __init__(self, n_estimators=30, max_depth=20, random_state=42, n_jobs=-1):
        """
        Random Forest para regresión multi-output (PTM e IPTM)
        """
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            n_jobs=n_jobs,
            #max_features='sqrt',         # Muy importante para alta dimensionalidad (1280)
            min_samples_leaf=2,          # Suaviza la predicción ante ruido estructural
            bootstrap=True,
            verbose=1   # muestra progreso de los árboles
        )

    def fit(self, X, y):
        print("\n🌲 Entrenando Random Forest...")
        print(f"Samples: {X.shape[0]}")
        print(f"Features: {X.shape[1]}")
        
        start = time.time()
        self.model.fit(X, y)
        end = time.time()
        
        print("✅ Entrenamiento terminado")
        print(f"⏱ Tiempo: {round(end - start, 2)} segundos")

    def predict(self, X):
        print("🔎 Generando predicciones con Random Forest...")
        return self.model.predict(X)

    def save(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self.model, path)
        print(f"💾 Modelo guardado en: {path}")

    def load(self, path):
        self.model = joblib.load(path)
        print(f"📂 Modelo cargado desde: {path}")