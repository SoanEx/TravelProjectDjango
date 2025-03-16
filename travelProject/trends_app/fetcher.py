# trends_app/fetcher.py
from pytrends.request import TrendReq
from trends_app.models import TrendData
from datetime import datetime

def fetch_google_trends(keyword="Taiwan travel", timeframe="today 3-m"):
    """
    使用 pytrends 取得指定關鍵字在指定時間範圍的搜尋熱度資料 (每日)。
    timeframe 範例: 'today 3-m' 表示最近 3 個月; 'today 12-m' 表示最近 12 個月; 'all' 表示全部年份
    回傳新增的筆數。
    """
    pytrends = TrendReq(hl='en-US', tz=360)  
    pytrends.build_payload(kw_list=[keyword], timeframe=timeframe, geo='')  

    df = pytrends.interest_over_time()
    # df.columns: [keyword, 'isPartial']
    # index: Date

    if df.empty:
        return 0

    df = df.reset_index()  # 讓 Date 成為一般欄位
    new_count = 0

    for _, row in df.iterrows():
        date_val = row['date'].date()  # row['date'] 是 Timestamp
        interest_val = int(row[keyword])
        # 跳過標記 isPartial 的行 (若 isPartial 為 True 表示當期數據可能尚未完整)
        # 也可視情況保留
        # if row['isPartial']:
        #     continue

        # 確認資料庫是否已存在該日期資料
        if not TrendData.objects.filter(keyword=keyword, date=date_val).exists():
            TrendData.objects.create(
                keyword=keyword,
                date=date_val,
                interest=interest_val
            )
            new_count += 1

    return new_count
