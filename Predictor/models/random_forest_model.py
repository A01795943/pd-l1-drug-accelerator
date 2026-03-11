from sklearn.ensemble import RandomForestRegressor
import joblib
import time


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
            verbose=1   # muestra progreso de los árboles
        )

    def fit(self, X, y):
        """
        Entrenar el modelo
        """

        print("\n🌲 Entrenando Random Forest...")
        print("Samples:", X.shape[0])
        print("Features:", X.shape[1])

        start = time.time()

        self.model.fit(X, y)

        end = time.time()

        print("✅ Entrenamiento terminado")
        print("⏱ Tiempo:", round(end - start, 2), "segundos")

    def predict(self, X):
        """
        Generar predicciones
        """

        print("🔎 Generando predicciones...")
        return self.model.predict(X)

    def save(self, path):
        """
        Guardar modelo entrenado
        """

        joblib.dump(self.model, path)
        print("💾 Modelo guardado en:", path)

    def load(self, path):
        """
        Cargar modelo entrenado
        """

        self.model = joblib.load(path)
        print("📂 Modelo cargado desde:", path)