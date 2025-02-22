from django.shortcuts import render

# Create your views here.
# travelProject/accounts/views.py

import random
import os

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

from .forms import RegistrationForm #驗證表單
from .forms import RegistrationLoginForm

def parse_e164_phone(country_code, local_phone):
    """
    嘗試將使用者輸入的「當地格式」轉為 E.164。
    country_code: "TW", "US" ...
    local_phone:  "0932170711"
    """
    # 假設我們先把它轉成類似 +國碼 + 號碼 (暫時拼接)
    # 這邊有多種寫法，也可 user 直接輸入 +886...
    if country_code == "TW":
        # 簡單示範: 若以0開頭，去0
        if local_phone.startswith('0'):
            local_phone = local_phone[1:]
        # 暫時拼成 +886
        phone_str = f"+886{local_phone}"
    elif country_code == "US":
        phone_str = f"+1{local_phone}"
    else:
        # 若其他國家先不處理
        phone_str = local_phone

    # 用 phonenumbers parse 來檢查是否有效 & 轉成 e164
    try:
        phone_obj = phonenumbers.parse(phone_str, None)
        if not phonenumbers.is_valid_number(phone_obj):
            # 不是有效號碼
            return None
        # 返回 e164 格式 e.g. +886932170711
        return phonenumbers.format_number(phone_obj, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        return None

def send_verification_code(phone_number, code):
    """
    呼叫 Twilio API 發送驗證碼到指定手機
    """
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
    """
    AJAX：檢查使用者是否已存在
    """
    username = request.GET.get('username', '').strip()
    exists = User.objects.filter(username=username).exists()
    return JsonResponse({'exists': exists})

def registration_login(request):
    context = {}

    if request.method == 'POST':
        step = request.POST.get('step', 'initial')

        if step == 'verify':
            # --- (1) 驗證碼步驟 ---
            input_code = request.POST.get('code')
            session_code = request.session.get('verification_code')
            if input_code == session_code:
                action = request.session.get('action')  # 'login', 'registration', or 'google'
                full_email = request.session.get('username')  # 這是完整 email (舉例: test@example.com)

                if action == 'registration':
                    # 建立新使用者
                    password = request.session.get('password')
                    # CHANGED: 將整個 email 拆成 @ 前後
                    username_part = full_email.split('@')[0]
                    
                    # CHANGED: 創建使用者時, username=拆後, email=完整
                    user = User.objects.create_user(
                        username=username_part,
                        email=full_email,
                        password=password
                    )
                    
                    # 處理手機號碼
                    e164_phone = request.session.get('e164_phone')
                    if e164_phone:
                        user.profile.phone_number = e164_phone
                        user.profile.save()
                    context['success'] = '恭喜註冊並驗證成功，您已登入。'

                elif action == 'google':
                    # Google OAuth
                    # 這裡的 session['username'] 應該也是一個 email
                    user_exists = User.objects.filter(username=full_email).exists()
                    if not user_exists:
                        # 如果你想同樣拆 email->username, email=完整, 可以這樣:
                        username_part = full_email.split('@')[0]
                        user = User.objects.create_user(
                            username=username_part,
                            email=full_email,
                            password=None
                        )
                        context['success'] = '以 Google 帳號註冊並驗證成功，您已登入。'
                    else:
                        user = User.objects.get(username=full_email)  
                        # 如果你仍以「整個 email 當 username」, 這裡就不拆了.
                        context['success'] = '以 Google 帳號登入並驗證成功。'

                else:
                    # action == 'login'
                    # 這裡 session['username'] 還是用 "整個 email"? 
                    # 如果先前 login 是用 email 當 username, 你要一致
                    user = User.objects.get(username=full_email)
                    context['success'] = '登入並驗證成功。'

                login(request, user)
                # 清 session
                for key in ['verification_code','action','username','password','e164_phone']:
                    request.session.pop(key, None)
            else:
                context['error'] = '驗證碼錯誤'
                context['show_verification'] = False

        else:
            # --- (2) 初始步驟 ---
            mode = request.POST.get('mode', 'normal')
            temp_username = request.POST.get('username', '').strip()
            # 1) 判斷帳號是否已存在 (這裡若 existing username=整個 email, 需一致)
            user_exists = User.objects.filter(username=temp_username).exists()

            # 2) 建立表單物件
            form = RegistrationLoginForm(user_exists=user_exists, data=request.POST)
            if not form.is_valid():
                # 表單驗證失敗
                context['error'] = form.errors.get_json_data()
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse(context)
                else:
                    return render(request, 'accounts/registration_login.html', context)

            # 3) 表單驗證通過，取得欄位
            full_email = form.cleaned_data['username']  # 這是整個 Email
            password = form.cleaned_data['password']
            country = form.cleaned_data['country']
            phone_local = form.cleaned_data['phone_local']

            # 4) 轉成 e164
            e164_phone = parse_e164_phone(country, phone_local)
            if not e164_phone:
                context['error'] = "電話格式不正確，請重新輸入"
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse(context)
                else:
                    return render(request, 'accounts/registration_login.html', context)
            request.session['e164_phone'] = e164_phone

            if mode == 'google':
                # Google OAuth
                token = request.POST.get('id_token')
                if not token:
                    context['error'] = '未取得 Google Token'
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse(context)
                    else:
                        return render(request, 'accounts/registration_login.html', context)

                try:
                    request_adapter = google.auth.transport.requests.Request()
                    id_info = google.oauth2.id_token.verify_oauth2_token(token, request_adapter, settings.GOOGLE_CLIENT_ID)
                    full_email = id_info['email']
                except ValueError:
                    context['error'] = 'Google 驗證失敗'
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse(context)
                    else:
                        return render(request, 'accounts/registration_login.html', context)

                verification_code = str(random.randint(100000, 999999))
                request.session['verification_code'] = verification_code
                request.session['action'] = 'google'
                request.session['username'] = full_email  # 整個 email

                try:
                    send_verification_code(e164_phone, verification_code)
                    context['show_verification'] = True
                    context['message'] = '已發送驗證碼至您的手機（Google 登入流程）。'
                except Exception as e:
                    context['error'] = f'簡訊發送失敗: {e}'

            else:
                # 一般登入/註冊流程
                if user_exists:
                    user = authenticate(username=full_email, password=password)
                    if user is None:
                        context['error'] = '密碼錯誤'
                        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                            return JsonResponse(context)
                        else:
                            return render(request, 'accounts/registration_login.html', context)
                    action = 'login'
                else:
                    action = 'registration'

                verification_code = str(random.randint(100000, 999999))
                request.session['verification_code'] = verification_code
                request.session['action'] = action
                request.session['username'] = full_email  # 整個 email
                request.session['password'] = password

                try:
                    send_verification_code(e164_phone, verification_code)
                    context['show_verification'] = True
                    context['message'] = '已發送驗證碼至您的手機。'
                except Exception as e:
                    context['error'] = f'簡訊發送失敗: {e}'

    # 決定回傳方式
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse(context)
    else:
        return render(request, 'accounts/registration_login.html', context)



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
            # 儲存使用者基本資料（email、username、密碼）
            user = form.save()
            # 取得經 parse_e164_phone 轉換後的手機號碼
            country = form.cleaned_data.get("country")
            phone_local = form.cleaned_data.get("phone_local")
            e164_phone = parse_e164_phone(country, phone_local)
            if e164_phone:
                # 假設你有使用 Profile 模型來存手機號碼
                user.profile.phone_number = e164_phone
                user.profile.save()
            # 登入使用者，並轉跳至成功頁或首頁
            login(request, user)
            return redirect('home')  # 例如轉跳到首頁
    else:
        form = RegistrationForm()
    return render(request, 'accounts/registration.html', {'form': form})

