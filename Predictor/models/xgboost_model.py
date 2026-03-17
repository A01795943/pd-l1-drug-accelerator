from xgboost import XGBRegressor
from sklearn.multioutput import MultiOutputRegressor
import joblib
import time
import os

class XGBoostModel:
    def __init__(self, n_estimators=200, learning_rate=0.05, max_depth=6, random_state=42):
        # Configuramos el modelo base de XGBoost
        base_model = XGBRegressor(
            n_estimators=n_estimators,
            learning_rate=learning_rate,
            max_depth=max_depth,
            random_state=random_state,
            objective='reg:squarederror',
            n_jobs=-1, # Usa todos los procesadores disponibles
            verbosity=1,
            tree_method='hist' # Método más rápido para datasets grandes
        )

        # MultiOutputRegressor permite predecir PTM e IPTM simultáneamente
        self.model = MultiOutputRegressor(base_model)

    def fit(self, X, y):
        print("\n🚀 Entrenando XGBoost...")
        start = time.time()
        
        self.model.fit(X, y)
        
        end = time.time()
        print("✅ XGBoost terminado")
        print(f"⏱ Tiempo: {round(end-start, 2)} seg")

    def predict(self, X):
        return self.model.predict(X)

    def save(self, path):
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self.model, path)
        print(f"💾 Modelo XGBoost guardado en: {path}")

    def load(self, path):
        if os.path.exists(path):
            self.model = joblib.load(path)
            print(f"📂 Modelo XGBoost cargado desde: {path}")
        else:
            print(f"⚠️ Error: El archivo {path} no existe.")