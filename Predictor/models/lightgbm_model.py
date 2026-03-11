import lightgbm as lgb
from sklearn.multioutput import MultiOutputRegressor
import joblib

class LightGBMModel:

    def __init__(self):

        base = lgb.LGBMRegressor(
            n_estimators=500,
            learning_rate=0.03,
            max_depth=8,
            subsample=0.9,
            colsample_bytree=0.8,
            random_state=42
        )

        self.model = MultiOutputRegressor(base)

    def fit(self,X,y):

        self.model.fit(X,y)

    def predict(self,X):

        return self.model.predict(X)

    def save(self,path):

        joblib.dump(self.model,path)