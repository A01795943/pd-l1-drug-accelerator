from xgboost import XGBRegressor
from sklearn.multioutput import MultiOutputRegressor
import joblib
import time


class XGBoostModel:

    def __init__(self, n_estimators=200, learning_rate=0.05, max_depth=6, random_state=42):

        base_model = XGBRegressor(
            n_estimators=n_estimators,
            learning_rate=learning_rate,
            max_depth=max_depth,
            random_state=random_state,
            objective='reg:squarederror',
            n_jobs=-1,
            verbosity=1
        )

        self.model = MultiOutputRegressor(base_model)

    def fit(self, X, y):

        print("\n🚀 Entrenando XGBoost...")

        start = time.time()

        self.model.fit(X, y)

        end = time.time()

        print("✅ XGBoost terminado")
        print("⏱ Tiempo:", round(end-start,2),"seg")

    def predict(self, X):

        return self.model.predict(X)

    def save(self, path):

        joblib.dump(self.model, path)

    def load(self, path):

        self.model = joblib.load(path)