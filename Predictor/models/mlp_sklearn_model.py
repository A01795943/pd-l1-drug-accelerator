from sklearn.neural_network import MLPRegressor
import joblib
import time
import os

class MLPModel:
    def __init__(self, hidden_layer_sizes=(512, 256, 128), max_iter=500, random_state=42):
        self.model = MLPRegressor(
            hidden_layer_sizes=hidden_layer_sizes,
            max_iter=max_iter,
            random_state=random_state,
            verbose=True
        )

    def fit(self, X, y):
        print("\n🧠 Entrenando MLP (Sklearn)...")
        start = time.time()
        self.model.fit(X, y)
        end = time.time()
        print("✅ MLP terminado")
        print(f"⏱ Tiempo: {round(end-start, 2)} seg")

    def predict(self, X):
        return self.model.predict(X)

    def save(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self.model, path)
        print(f"💾 Modelo MLP guardado en: {path}")

    def load(self, path):
        self.model = joblib.load(path)
        print(f"📂 Modelo MLP cargado desde: {path}")