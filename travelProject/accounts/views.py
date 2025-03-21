# travelProject/accounts/views.py

import random
import os

import uuid
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.conf import settings
from twilio.rest import Client

# Google OAuth 驗證相關
import google.auth.transport.requests
import google.oauth2.id_token

import phonenumbers

from .forms import RegistrationForm  # 驗證表單
from .forms import RegistrationLoginForm

from django.db.models import Q
from accounts.models import Profile


def parse_e164_phone(country_code, local_phone):
    # 省略同前，維持你的 parse e164 邏輯
    if country_code == "TW":
        if local_phone.startswith('0'):
            local_phone = local_phone[1:]
        phone_str = f"+886{local_phone}"
    elif country_code == "US":
        phone_str = f"+1{local_phone}"
    else:
        phone_str = local_phone
    try:
        phone_obj = phonenumbers.parse(phone_str, None)
        if not phonenumbers.is_valid_number(phone_obj):
            return None
        return phonenumbers.format_number(phone_obj, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        return None


def send_verification_code(phone_number, code):
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=f"您的驗證碼是：{code}",
        from_=settings.TWILIO_PHONE_NUMBER,
        to=phone_number
    )
    return message.sid


def check_username(request):
    username = request.GET.get('username', '').strip()
    exists = User.objects.filter(username=username).exists()
    return JsonResponse({'exists': exists})


def registration_login(request):
    """
    1. step=initial (初次 POST)：
       - if mode=google => 走 Google 驗證邏輯
       - else => 走一般表單 (RegistrationLoginForm) 驗證
    2. step=verify => 驗證簡訊碼
    """
    context = {}

    if request.method == 'POST':
        step = request.POST.get('step', 'initial')

        if step == 'verify':
            # --- 驗證碼步驟 ---
            input_code = request.POST.get('code')
            session_code = request.session.get('verification_code', '')
            if input_code == session_code:
                # 驗證成功
                full_email = request.session.get('username')
                user = User.objects.get(username=full_email)

                # phone_verified = True
                user.profile.phone_verified = True
                user.profile.save()

                # 將 device_id 加入 known_devices
                device_id = request.session.get('device_id')
                if device_id:
                    user.profile.add_known_device(device_id)

                # 登入並清除 session
                login(request, user)
                for key in ['verification_code','username','password','e164_phone','device_id']:
                    request.session.pop(key, None)

                context['success'] = '驗證成功，已登入。'
            else:
                context['error'] = '驗證碼錯誤'

        else:
            # --- 初始步驟 ---
            mode = request.POST.get('mode', 'normal')
            device_id = request.POST.get('device_id')
            if not device_id:
                device_id = str(random.randint(10000000, 99999999))
            request.session['device_id'] = device_id

            if mode == 'google':
                # (A) Google One Tap 登入流程，不要檢查一般表單
                token = request.POST.get('id_token')
                if not token:
                    context['error'] = '未取得 Google Token'
                    return _smart_return(request, context)

                # 驗證 Token
                try:
                    req = google.auth.transport.requests.Request()
                    id_info = google.oauth2.id_token.verify_oauth2_token(token, req, settings.GOOGLE_CLIENT_ID)
                    full_email = id_info['email']
                except ValueError:
                    context['error'] = 'Google 驗證失敗'
                    return _smart_return(request, context)

                # 假設你也需要手機 (country, phone_local)
                country = request.POST.get('country', 'TW')
                phone_local = request.POST.get('phone_local', '')
                if not phone_local:
                    context['error'] = "尚未填寫手機號碼"
                    context['ask_phone'] = True
                    return _smart_return(request, context)
                e164_phone = parse_e164_phone(country, phone_local)

                request.session['username'] = full_email
                request.session['e164_phone'] = e164_phone

                # 是否已有此帳號？
                user_exists = User.objects.filter(username=full_email).exists()
                if not user_exists:
                    # 建立新用戶
                    user = User.objects.create_user(
                        username=full_email,
                        email=full_email,
                        password=None  # Google 帳號不需本地密碼
                    )
                    user.profile.phone_number = e164_phone or ""
                    user.profile.phone_verified = False
                    user.profile.save()
                    need_sms_verify = True
                else:
                    user = User.objects.get(username=full_email)
                    known_devices = user.profile.get_known_devices()
                    need_sms_verify = (not user.profile.phone_verified) or (device_id not in known_devices)

                if need_sms_verify:
                    verification_code = str(random.randint(100000, 999999))
                    request.session['verification_code'] = verification_code
                    try:
                        if e164_phone:
                            send_verification_code(e164_phone, verification_code)
                            context['show_verification'] = True
                            context['message'] = 'Google 帳號首次/新裝置登入，需要簡訊驗證。'
                        else:
                            context['error'] = "尚未填寫手機號碼，無法發送簡訊。"
                    except Exception as e:
                        context['error'] = f'簡訊發送失敗: {e}'
                else:
                    # 不需要驗證 => 直接登入
                    login(request, user)
                    user.profile.add_known_device(device_id)
                    context['success'] = 'Google 登入成功 (手機已驗證)。'

                return _smart_return(request, context)

            else:
                # (B) 一般登入/註冊流程 => 檢查表單
                temp_username = request.POST.get('username', '').strip()
                user_exists = User.objects.filter(username=temp_username).exists()

                form = RegistrationLoginForm(user_exists=user_exists, data=request.POST)
                if not form.is_valid():
                    context['error'] = form.errors.get_json_data()
                    return _smart_return(request, context)

                full_email = form.cleaned_data['username']
                password = form.cleaned_data['password']
                country = form.cleaned_data['country']
                phone_local = form.cleaned_data['phone_local']

                e164_phone = parse_e164_phone(country, phone_local)
                if not e164_phone:
                    context['error'] = "電話格式不正確，請重新輸入"
                    return _smart_return(request, context)

                # 存進 session
                request.session['username'] = full_email
                request.session['e164_phone'] = e164_phone
                request.session['password'] = password

                if user_exists:
                    user = authenticate(username=full_email, password=password)
                    if user is None:
                        context['error'] = '密碼錯誤'
                        return _smart_return(request, context)

                    known_devices = user.profile.get_known_devices()
                    if (not user.profile.phone_verified) or (device_id not in known_devices):
                        # 需要簡訊
                        verification_code = str(random.randint(100000, 999999))
                        request.session['verification_code'] = verification_code
                        try:
                            send_verification_code(e164_phone, verification_code)
                            context['show_verification'] = True
                            context['message'] = '已發送驗證碼至您的手機。'
                        except Exception as e:
                            context['error'] = f'簡訊發送失敗: {e}'
                    else:
                        # 直接登入
                        login(request, user)
                        user.profile.add_known_device(device_id)
                        context['success'] = '已成功登入。'
                else:
                    # 新用戶 => 建立 + phone_verified=False => 簡訊驗證
                    user = User.objects.create_user(username=full_email, email=full_email, password=password)
                    user.profile.phone_number = e164_phone
                    user.profile.phone_verified = False
                    user.profile.save()

                    verification_code = str(random.randint(100000, 999999))
                    request.session['verification_code'] = verification_code
                    try:
                        send_verification_code(e164_phone, verification_code)
                        context['show_verification'] = True
                        context['message'] = '已發送驗證碼至您的手機 (新註冊)。'
                    except Exception as e:
                        context['error'] = f'簡訊發送失敗: {e}'

    # GET 或處理完後
    return _smart_return(request, context)

def google_auth_verify(request):
    """
    範例：若你要單獨測試 Google OAuth，或做其他延伸時可用
    暫時留空或供後端 API 用
    """
    return JsonResponse({'msg': 'OK'})


def test_twilio(request):
    phone = "+886932170711"  # 測試號碼
    code = "123456"
    try:
        send_verification_code(phone, code)
    except Exception as e:
        return HttpResponse(f"錯誤: {str(e)}")
    return HttpResponse("已嘗試發送簡訊")


def registration_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # 取得經 parse_e164_phone 轉換後的手機號碼
            country = form.cleaned_data.get("country")
            phone_local = form.cleaned_data.get("phone_local")
            e164_phone = parse_e164_phone(country, phone_local)
            if e164_phone:
                user.profile.phone_number = e164_phone
                user.profile.save()
            login(request, user)
            return redirect('home')  # 例如轉跳到首頁
    else:
        form = RegistrationForm()
    return render(request, 'accounts/registration.html', {'form': form})


def _smart_return(request, context):
    """
    小工具函式：若是 AJAX 就 JsonResponse；否則 render
    """
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse(context)
    else:
        context['GOOGLE_CLIENT_ID'] = settings.GOOGLE_CLIENT_ID
        return render(request, 'accounts/registration_login.html', context)


def google_oauth_verify(request):
    return JsonResponse({'msg': 'OK'})

def google_redirect_callback(request):
    # 若你完全改用 One Tap，就不需要 redirect flow，此函式可刪除或保留備用
    return HttpResponse("已棄用 redirect flow，可改用 One Tap。")

def index_view(request):
    return render(request, 'index.html')

def create_guest_user():
    # 產生「guest_隨機8碼」的 username
    random_username = f"guest_{uuid.uuid4().hex[:8]}"
    
    # password=None 表示不給任何密碼（僅能用程式自動登入）
    user = User.objects.create_user(username=random_username, password=None)
    
    # 設定 Profile 為 guest
    user.profile.is_guest = True
    user.profile.save()
    
    return user

def search_user_view(request):
    keyword = request.GET.get('q', '').strip()

    queryset = User.objects.filter(is_staff=False, is_superuser=False)

    if keyword:
        queryset = queryset.filter(
            Q(username__icontains=keyword) |
            Q(profile__phone_number__icontains=keyword)
        )

    return render(request, 'accounts/user_search_result.html', {
        'results': queryset,
        'keyword': keyword
    })