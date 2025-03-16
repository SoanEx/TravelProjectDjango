# trends_app/ml_utils.py
import numpy as np
from sklearn.linear_model import LinearRegression
import joblib
import os
from django.conf import settings
from trends_app.models import TrendData
from sklearn.metrics import mean_squared_error, r2_score

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

# -----------------------------
# 2. 新增函式: evaluate_model
# -----------------------------
def evaluate_model(keyword="Taiwan travel", window_size=7, train_ratio=0.8):
    """
    新函式: 先做簡易的訓練-測試切分，計算 MSE / R2 分數，
    並將測試對比資料一併回傳
    """
    qs = TrendData.objects.filter(keyword=keyword).order_by('date')
    if qs.count() < window_size + 1:
        return {
            'success': False,
            'message': '資料量不足，無法進行評估'
        }

    # 將 interest 數值取出
    interests = [obj.interest for obj in qs]
    dates = [obj.date for obj in qs]

    # 產生窗格特徵
    X_all, y_all = [], []
    for i in range(window_size, len(interests)):
        past_features = interests[i - window_size:i]
        X_all.append(past_features)
        y_all.append(interests[i])

    X_all = np.array(X_all)
    y_all = np.array(y_all)
    date_all = dates[window_size:]

    train_size = int(len(X_all) * train_ratio)
    if train_size <= 0 or train_size >= len(X_all):
        return {
            'success': False,
            'message': 'train_ratio 不合理，無法切分'
        }

    # 切分訓練 / 測試集
    X_train, X_test = X_all[:train_size], X_all[train_size:]
    y_train, y_test = y_all[:train_size], y_all[train_size:]
    date_test = date_all[train_size:]

    # 建立並訓練
    model = LinearRegression()
    model.fit(X_train, y_train)

    # 可選: 存檔 (若需要覆蓋舊的 model)
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    # 測試預測
    y_pred = model.predict(X_test)
    mse_val = mean_squared_error(y_test, y_pred)
    r2_val = r2_score(y_test, y_pred)

    # 整理測試對比列表
    compare_list = []
    for i in range(len(y_test)):
        compare_list.append({
            'date': str(date_test[i]),
            'actual': float(y_test[i]),
            'predicted': float(y_pred[i])
        })

    return {
        'success': True,
        'message': '評估完成',
        'mse': mse_val,
        'r2': r2_val,
        'test_count': len(X_test),
        'compare': compare_list  # 依需求可只回傳前幾筆
    }