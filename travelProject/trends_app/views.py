# trends_app/views.py
from django.http import JsonResponse
from django.shortcuts import render, redirect
from trends_app.fetcher import fetch_google_trends
from trends_app.ml_utils import train_model, predict_future, evaluate_model
from trends_app.models import TrendData
from datetime import datetime
import json

def index(request):
    """
    首頁視圖: 顯示目前資料庫中的歷史資料 (最近30~60筆),
    並在前端繪製圖表(歷史 + 預測).
    """
    keyword = request.GET.get('keyword', 'Taiwan travel')
    qs = TrendData.objects.filter(keyword=keyword).order_by('date')
    data_count = qs.count()
    show_count = 60 if data_count > 60 else data_count
    recent_data = qs[data_count - show_count:]

    dates_list = [str(obj.date) for obj in recent_data]
    interests_list = [obj.interest for obj in recent_data]

    context = {
        'keyword': keyword,
        'dates_json': json.dumps(dates_list),
        'interests_json': json.dumps(interests_list)
    }
    return render(request, 'trends_app/index.html', context)


def fetch_data_view(request):
    """
    透過 Pytrends 抓取資料, 寫入資料庫. 回傳新增筆數.
    """
    keyword = request.GET.get('keyword', 'Taiwan travel')
    timeframe = request.GET.get('timeframe', 'today 3-m')
    new_count = fetch_google_trends(keyword, timeframe)
    return JsonResponse({'status': 'ok', 'new_count': new_count})


def train_model_view(request):
    """
    觸發模型訓練
    """
    keyword = request.GET.get('keyword', 'Taiwan travel')
    success = train_model(keyword=keyword, window_size=7)
    return JsonResponse({'status': 'ok' if success else 'fail'})


def predict_view(request):
    """
    以已訓練的模型預測未來7天, 直接以 JSON 格式回傳
    """
    keyword = request.GET.get('keyword', 'Taiwan travel')
    predictions = predict_future(keyword=keyword, window_size=7, days_to_predict=7)
    # predictions 為 [(date, interest), ...]
    pred_list = []
    for d, val in predictions:
        pred_list.append({'date': str(d), 'interest': val})
    return JsonResponse({'status': 'ok', 'predictions': pred_list})


def evaluate_model_view(request):
    """
    新方法 - 評估模型 (包含訓練/測試分割, 計算 MSE, R2)
    """

    # 1) 如果沒有帶 keyword，就顯示模板 (適用於第一次進入頁面)
    if 'keyword' not in request.GET:
        return render(request, 'trends_app/evaluate.html')

    # 2) 有帶 keyword，但判斷是否為空
    keyword = request.GET.get('keyword', '').strip()
    if not keyword:
        return JsonResponse({
            'success': False,
            'message': '請輸入關鍵字！(後端檢查)'
        })

    # 3) 取得 window_size, train_ratio
    try:
        window_size = int(request.GET.get('window_size', 7))
        train_ratio = float(request.GET.get('train_ratio', 0.8))
    except ValueError:
        return JsonResponse({
            'success': False,
            'message': 'window_size 或 train_ratio 格式有誤，請輸入正確的數字！'
        })

    # 4) 檢查資料庫是否有足夠資料
    qs = TrendData.objects.filter(keyword=keyword).order_by('date')
    if qs.count() < window_size:
        return JsonResponse({
            'success': False,
            'message': f'關鍵字「{keyword}」的資料筆數不足，無法以 window_size={window_size} 進行評估。'
        })

    # 5) 進行評估：加上 try/except，避免程式內部拋出未捕捉的錯誤
    try:
        result = evaluate_model(keyword=keyword, window_size=window_size, train_ratio=train_ratio)
        # result 結構:
        # {
        #   'success': bool,
        #   'message': str,
        #   'mse': float,
        #   'r2': float,
        #   'test_count': int,
        #   'compare': [ {date, actual, predicted}, ... ]
        # }

        # 若 evaluate_model 回傳的 success=False，也應同樣回傳前端提示
        if not result.get('success', False):
            return JsonResponse(result)

        # 沒問題的話，以 JSON 回傳
        return JsonResponse(result, safe=False)

    except Exception as e:
        # 捕捉任何在 evaluate_model 過程中的意外錯誤
        return JsonResponse({
            'success': False,
            'message': f'評估過程中發生錯誤：{str(e)}'
        })
