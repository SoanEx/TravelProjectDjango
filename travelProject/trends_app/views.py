# trends_app/views.py
from django.http import JsonResponse, HttpResponseBadRequest
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
    keyword   = request.GET.get("keyword", "").strip()
    timeframe = request.GET.get("timeframe", "today 3-m").strip()

    if not keyword:
        return HttpResponseBadRequest("keyword is required")

    preds = predict_future(
        keyword=keyword,
        window_size=7,
        days_to_predict=7,
        force_refresh=True,       # ★ 強迫重新抓 ★
        timeframe=timeframe
    )

    pred_list = [{"date": str(d), "interest": val} for d, val in preds]
    return JsonResponse({"status": "ok",
                         "keyword": keyword,
                         "timeframe": timeframe,
                         "predictions": pred_list})


def evaluate_model_view(request):
    # 1) 首次進頁面只渲染模板
    if 'keyword' not in request.GET:
        return render(request, 'trends_app/evaluate.html')

    # 2) 取關鍵字與 timeframe（新增）
    keyword   = request.GET.get('keyword', '').strip()
    timeframe = request.GET.get('timeframe', 'today 3-m').strip()
    if not keyword:
        return JsonResponse({'success': False, 'message': '請輸入關鍵字！'})

    # 3) 取其它參數
    try:
        window_size = int(request.GET.get('window_size', 7))
        train_ratio = float(request.GET.get('train_ratio', 0.8))
    except ValueError:
        return JsonResponse({'success': False, 'message': 'window_size 或 train_ratio 格式錯誤'})

    # 4) 強制補資料 ── 抓不到直接回錯
    try:
        fetch_google_trends(keyword=keyword, timeframe=timeframe)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'抓取失敗：{e}'})

    # 5) 再檢查資料量
    qs = TrendData.objects.filter(keyword=keyword).order_by('date')
    if qs.count() < window_size + 1:          # 多留一天才有 y 值
        return JsonResponse({'success': False,
                             'message': f'「{keyword}」資料不足，window_size={window_size} 無法評估'})

    # 6) 評估（附 try/except）
    try:
        result = evaluate_model(keyword=keyword,
                                window_size=window_size,
                                train_ratio=train_ratio)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'評估錯誤：{e}'})
