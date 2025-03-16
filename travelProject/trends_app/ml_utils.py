# trends_app/ml_utils.py
import numpy as np
from sklearn.linear_model import LinearRegression
import joblib
import os
from django.conf import settings
from trends_app.models import TrendData

MODEL_DIR = os.path.join(settings.BASE_DIR, 'ml_models')
MODEL_PATH = os.path.join(MODEL_DIR, 'trend_model.pkl')

def train_model(keyword="Taiwan travel", window_size=7):
    """
    從資料庫讀取指定關鍵字的歷史記錄，使用前 window_size 天的 interest 預測第 (window_size+1) 天的 interest。
    """
    # 取得該關鍵字的資料，按日期排序
    qs = TrendData.objects.filter(keyword=keyword).order_by('date')
    if len(qs) < window_size + 1:
        return False  # 資料量不足，無法訓練

    # 準備訓練集
    interests = [obj.interest for obj in qs]
    X, y = [], []
    for i in range(window_size, len(interests)):
        # 取前 window_size 天當特徵
        features = interests[i-window_size:i]  # list of length window_size
        X.append(features)
        y.append(interests[i])

    # 轉 numpy array
    X = np.array(X)
    y = np.array(y)

    # 建立線性回歸模型 (可換成其他回歸算法)
    model = LinearRegression()
    model.fit(X, y)

    # 模型目錄
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    return True

def predict_future(keyword="Taiwan travel", window_size=7, days_to_predict=7):
    """
    使用已訓練的模型，預測未來 days_to_predict 天的 interest。
    回傳 [(date, predicted_interest), ...]
    """
    # 先載入模型
    if not os.path.exists(MODEL_PATH):
        return []

    model = joblib.load(MODEL_PATH)

    # 找出該關鍵字現有資料中最新的 window_size 天 interest
    qs = TrendData.objects.filter(keyword=keyword).order_by('date')
    if len(qs) < window_size:
        return []  # 資料不足

    # 取得最新的 window_size 筆 interest
    interests = [obj.interest for obj in qs]
    last_window = interests[-window_size:]  # list, length=window_size

    # 取得最新日期
    last_date = qs.last().date

    from datetime import timedelta
    predictions = []

    current_features = np.array(last_window)

    for i in range(days_to_predict):
        # 做 1 天預測
        pred_interest = model.predict(current_features.reshape(1, -1))[0]
        # 預測的日期 = last_date + i+1
        pred_date = last_date + timedelta(days=i+1)
        predictions.append((pred_date, int(pred_interest)))

        # 更新特徵: 去頭 + 加入新預測
        current_features = np.roll(current_features, -1)
        current_features[-1] = pred_interest

    return predictions
