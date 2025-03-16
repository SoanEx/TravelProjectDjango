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
    首頁視圖: 顯示目前資料庫中的歷史資料 (最近30筆),
    並在前端繪製圖表(歷史 + 預測).
    """
    keyword = request.GET.get('keyword', 'Taiwan travel')
    # 抓出該關鍵字的資料, 依日期排序
    qs = TrendData.objects.filter(keyword=keyword).order_by('date')
    # 只取最近 30 ~ 60 筆繪圖, 避免資料過多導致圖表擁擠
    data_count = qs.count()
    show_count = 60 if data_count > 60 else data_count
    recent_data = qs[data_count - show_count:]

    dates_list = [str(obj.date) for obj in recent_data]
    interests_list = [obj.interest for obj in recent_data]


    # 準備給模板或前端 JS 的資料
    dates = [str(obj.date) for obj in recent_data]
    interests = [obj.interest for obj in recent_data]

    context = {
        'keyword': keyword,
        'dates_json': json.dumps(dates_list),       # <— JSON 字串
        'interests_json': json.dumps(interests_list)
    }
    print(dates_list[:5])
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
    # 改成可 JSON 化的陣列
    pred_list = []
    for d, val in predictions:
        pred_list.append({'date': str(d), 'interest': val})
    return JsonResponse({'status': 'ok', 'predictions': pred_list})

# ---------------------------------
# 新增視圖: evaluate_model_view
# ---------------------------------
def evaluate_model_view(request):
    """
    新方法 - 評估模型 (包含訓練/測試分割, 計算 MSE, R2)
    """
    keyword = request.GET.get('keyword', '').strip()
    if 'keyword' not in request.GET:
        # 表示第一次進入 /evaluate/，沒有帶參數 => 渲染頁面
        return render(request, 'trends_app/evaluate.html')

    # 否則，就代表前端帶了 keyword(即使是空字串)
    keyword = request.GET.get('keyword', '').strip()
    if not keyword:
        # 有帶參數，但內容為空 => 回傳 JSON 提醒
        return JsonResponse({
            'success': False,
            'message': '請輸入關鍵字！(後端檢查)'
        }, safe=False)
    
    # Case 2: 有帶參數 => 執行評估
    window_size = int(request.GET.get('window_size', 7))
    train_ratio = float(request.GET.get('train_ratio', 0.8))

    result = evaluate_model(keyword=keyword, window_size=window_size, train_ratio=train_ratio)
    # result 結構:
    # {
    #   'success': bool,
    #   'message': str,
    #   'mse': float,
    #   'r2': float,
    #   'test_count': int,
    #   'compare': [ {date,actual,predicted}, ... ]
    # }
    # 我們可以將其帶到新 evaluate.html，或直接以 JSON 回傳

    

    # 若想在 HTML 顯示，就 render
    return JsonResponse(result, safe=False)