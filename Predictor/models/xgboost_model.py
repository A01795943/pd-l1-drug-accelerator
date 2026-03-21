from xgboost import XGBRegressor
from sklearn.multioutput import MultiOutputRegressor
import joblib
import time
import os

class XGBoostModel:
    def __init__(self, 
                 n_estimators=6000,       # Actualizado estaba en 200, 400, 2000
                 max_depth=10,            # Actualizado estaba en 6, 8, 10
                 learning_rate=0.005,      # se mantuvo estaba 0,05, 0,02
                 subsample=0.85,          # Nuevo parámetro añadido, 
                 colsample_bytree=0.15,   # Nuevo parámetro añadido
                 min_child_weight=5,      # Evita hojas con muy poca cobertura, añadido
                 random_state=42):
        
        # Configuramos el modelo base de XGBoost con tus nuevos parámetros
        base_model = XGBRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            subsample=subsample,
            colsample_bytree=colsample_bytree,
            min_child_weight=min_child_weight,

            # --- AGREGADOS DE REGULARIZACIÓN ---
            gamma=0.1,               # Penaliza árboles que no aportan mucho (evita estancamiento)
            reg_alpha=0.1,           # Regularización L1 (ayuda a la selección de rasgos)
            reg_lambda=1.5,          # Regularización L2 (evita pesos extremos)
            
            # Parámetros técnicos fijos
            random_state=random_state,
            objective='reg:squarederror',
            n_jobs=-1, 
            verbosity=0,
            tree_method='hist' 
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