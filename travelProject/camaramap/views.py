from django.shortcuts import render
import json
import pandas as pd
from django.http import JsonResponse
from django.shortcuts import render
from geopy.distance import geodesic
import os


# Create your views here.

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

def map_view(request):
    """ 顯示 Google 地圖頁面 """
    return render(request, 'dynamicmap.html')


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
