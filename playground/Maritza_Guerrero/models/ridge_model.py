from sklearn.linear_model import Ridge
import joblib
import time


class RidgeModel:

    def __init__(self, alpha=1.0):
        self.model = Ridge(alpha=alpha)

    def fit(self, X, y):

        print("\n📈 Entrenando Ridge...")

        start = time.time()

        self.model.fit(X, y)

        end = time.time()

        print("✅ Ridge terminado")
        print("⏱ Tiempo:", round(end-start,2),"seg")

    def predict(self, X):

        print("🔎 Prediciendo con Ridge...")
        return self.model.predict(X)

    def save(self, path):

        joblib.dump(self.model, path)
        print("💾 Modelo guardado:", path)

    def load(self, path):

        self.model = joblib.load(path)