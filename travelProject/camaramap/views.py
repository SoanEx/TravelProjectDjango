from django.shortcuts import render
import json
import pandas as pd
from django.http import JsonResponse
from geopy.distance import geodesic
import os
from django.conf import settings
import requests
import openai
import time
from dotenv import load_dotenv
from django.views.decorators.csrf import csrf_exempt
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage


# Create your views here.
load_dotenv()  # 載入 .env 變數
# 讀取測速照相 CSV 檔案
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMERA_CSV_PATH = os.path.join(BASE_DIR, "camaramap", "speed_cameras.csv")
# CAMERA_CSV_PATH = "camaramap/speed_cameras.csv"  # 請放入你的 CSV 檔案路徑


def load_speed_cameras():
    """ 讀取測速照相 CSV 並修正欄位名稱 """
    print(f"📂 嘗試讀取檔案: {CAMERA_CSV_PATH}")

    if not os.path.exists(CAMERA_CSV_PATH):
        raise FileNotFoundError(f"❌ 找不到測速相機 CSV 檔案: {CAMERA_CSV_PATH}")

    # 讀取 CSV，顯示原始欄位名稱
    df = pd.read_csv(CAMERA_CSV_PATH, encoding="utf-8")

    print("📊 讀取 CSV 成功，原始欄位名稱:", df.columns.tolist())  # Debug 顯示欄位名稱

    # **關鍵步驟：將欄位名稱轉小寫並去除空格**
    df.columns = df.columns.str.strip().str.lower()
    
    print("🔍 修正後的欄位名稱:", df.columns.tolist())  # Debug 檢查修正後的欄位名稱

    # 自動修正欄位名稱
    column_mapping = {
        "latitude": "latitude",
        "longitude": "longitude"
    }
    df.rename(columns=column_mapping, inplace=True)

    # 確保 `latitude` & `longitude` 存在
    required_columns = {'latitude', 'longitude'}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"❌ CSV 欄位錯誤，找到的欄位: {df.columns.tolist()}，應包含: {list(required_columns)}")

    # 轉換 `latitude` & `longitude` 為數字
    df['latitude'] = pd.to_numeric(df["latitude"], errors='coerce')
    df['longitude'] = pd.to_numeric(df["longitude"], errors='coerce')

    print(f"✅ 清理後的測速相機數據: {len(df)} 筆")

    cameras = df[['latitude', 'longitude']].dropna().to_dict(orient='records')
    return cameras

def filter_cameras_near_route(route_points, cameras, max_distance=0.1):
    """ 篩選出距離路線 100 公尺 (0.1 km) 內的測速照相點 """
    filtered_cameras = []

    for camera in cameras:
        cam_location = (camera['latitude'], camera['longitude'])
        # 檢查相機是否在路線附近
        for route_point in route_points:
            route_location = (route_point['lat'], route_point['lng'])
            if geodesic(cam_location, route_location).km < max_distance:
                filtered_cameras.append(camera)
                break  # 找到符合條件的就加入，避免重複

    return filtered_cameras

def get_google_maps_key(request):
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return JsonResponse({"error": "API key not found"}, status=500)
    return JsonResponse({"apiKey": api_key})

def map_view(request):
    """ 顯示 Google 地圖頁面 """
    # return render(request, 'dynamicmap.html')
    return render(request, 'camaramap/index.html')  


def get_speed_cameras(request):
    """ 接收 AJAX 請求，回傳符合路線的測速照相點 """
    try:
        print("✅ 收到請求")  # Debug
        print("🔹 Request Body:", request.body)

        # 嘗試解析 JSON
        data = json.loads(request.body)
        print("🔹 解析 JSON 成功:", data)

        route_points = data.get('route', [])
        if not route_points:
            return JsonResponse({'error': '沒有接收到路線點'}, status=400)

        # 讀取測速相機資料
        all_cameras = load_speed_cameras()
        print(f"🔹 總共有 {len(all_cameras)} 個測速相機")

        # 篩選符合條件的測速相機
        filtered_cameras = filter_cameras_near_route(route_points, all_cameras)
        print(f"✅ 符合條件的測速相機: {len(filtered_cameras)} 個")

        return JsonResponse({'cameras': filtered_cameras})

    except json.JSONDecodeError as e:
        print("❌ JSON 解析錯誤:", e)
        return JsonResponse({'error': 'JSON 格式錯誤'}, status=400)

    except FileNotFoundError as e:
        print("❌ 找不到測速相機 CSV 檔案:", e)
        return JsonResponse({'error': '測速相機資料缺失'}, status=500)

    except Exception as e:
        print("❌ 其他錯誤:", e)
        return JsonResponse({'error': str(e)}, status=500)
    
def get_nearby_places(request):
    lat = request.GET.get("lat")
    lng = request.GET.get("lng")
    keyword = request.GET.get("keyword", "tourist attraction")

    if not lat or not lng:
        return JsonResponse({"error": "缺少經緯度參數"}, status=400)

    
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius=5000&type=point_of_interest&keyword={keyword}&key={settings.GOOGLE_MAPS_API_KEY}"
    print(f"🔍 Google Places API 請求: {url}")  # Debug
    response = requests.get(url)
    data = response.json()

    if "error_message" in data:
        print(f"❌ API 錯誤: {data['error_message']}")
        return JsonResponse({"error": data["error_message"]}, status=500)

    return JsonResponse({"places": data.get("results", [])})


def generate_itinerary(request):
    
    location = request.GET.get("location")
    days = int(request.GET.get("days", 1))

    prompt = f"請根據 {location} 為 {days} 天規劃最佳旅遊行程，包含景點、活動、餐飲推薦。"
    
    openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    time.sleep(5)
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}]
    )
    response_data = response.choices[0].message.content if response.choices else "無法生成行程"
    return JsonResponse({"itinerary": response_data})

# 初始化 LINE Bot API
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
# OpenWeatherMap API URL
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"

@csrf_exempt
def line_webhook(request):
    """ 處理來自 LINE 的 Webhook 請求 """
    if request.method == "POST":
        signature = request.headers.get("X-Line-Signature")
        body = request.body.decode("utf-8")

        try:
            # ✅ 初始化 LINE WebhookHandler
            handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
            handler.handle(body, signature)

            events = json.loads(body)["events"]
            for event in events:
                if isinstance(event, MessageEvent) and isinstance(event.message, TextMessage):
                    city = event.message.text
                    weather_info = get_weather(city)

                    reply_message = f"📍 {city} 天氣：\n{weather_info}"
                    
                    # ✅ 使用 `reply_message()` 而非 `push_message()`
                    line_bot_api.reply_message(
                        event.reply_token, TextSendMessage(text=reply_message)
                    )

            return JsonResponse({"status": "success"})
        except InvalidSignatureError:
            return JsonResponse({"error": "Invalid signature"}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=400)

def get_weather(city):
    """ 使用 OpenWeatherMap API 查詢天氣 """
    params = {
        "q": city,
        "appid": os.getenv("OPENWEATHER_API_KEY"),
        "units": "metric",
        "lang": "zh_tw"
    }
    response = requests.get(WEATHER_API_URL, params=params)
    data = response.json()

    if response.status_code == 200 and "main" in data:
        temp = data["main"]["temp"]
        weather = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        return f"🌡 溫度: {temp}°C\n☁ 天氣: {weather}\n💧 濕度: {humidity}%"
    elif "message" in data:
        return f"❌ 錯誤: {data['message']}"
    else:
        return "❌ 找不到該城市的天氣資訊，請確認城市名稱是否正確！"

def google_translate(text, target="zh-TW"):
    """ 使用 Google 翻譯 API 將文字翻譯成指定語言 """
    GOOGLE_TRANSLATE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")  
    url = f"https://translation.googleapis.com/language/translate/v2"
    
    params = {
        "q": text,
        "target": target,
        "key": GOOGLE_TRANSLATE_API_KEY
    }
    
    response = requests.post(url, data=params)
    result = response.json()

    if "data" in result and "translations" in result["data"]:
        return result["data"]["translations"][0]["translatedText"]
    return text  # 若翻譯失敗則回傳原始文字

def translate_text_api(request):
    text = request.GET.get("text", "")
    target = request.GET.get("target", "zh-TW")
    
    if not text:
        return JsonResponse({"error": "請提供要翻譯的文本"}, status=400)

    translated_text = google_translate(text, target)
    return JsonResponse({"translatedText": translated_text})

