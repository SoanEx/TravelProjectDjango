"""
URL configuration for travelProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from accounts.views import index_view
from camaramap import views
from personalPage import views as personalPage_views
from camaramap.views import line_webhook

urlpatterns = [
    path('admin/', admin.site.urls),
    # 將 accounts 的路由接在某個 prefix，例如 /accounts/
    path('accounts/', include('accounts.urls')),
    path('', index_view, name='home'),
    path('accounts/', include('django.contrib.auth.urls')),## 這行很重要：包含 Django 內建的帳號相關 URLs (包含 login/logout/password_reset...)
    path("bk/",include('bookkeeping.urls')),
    path('map/', views.map_view, name='map_page'),
    path('api/get_speed_cameras/', views.get_speed_cameras, name='get_speed_cameras'),
    path('api/nearby_places/', views.get_nearby_places, name='get_nearby_places'),
    path('itinerary/', views.generate_itinerary, name='generate_itinerary'),
    path("get_google_maps_key/", views.get_google_maps_key, name="get_google_maps_key"),
    path('funstuff/', include('funstuff.urls')),
    path('trends/', include('trends_app.urls')),  #拖尾逗號
    path('personalPage/', personalPage_views.personal_page, name='personal_page'),
    path("line/webhook/", line_webhook, name="line_webhook"),
    path("api/translate/", views.translate_text_api, name="translate_text_api"),
    path("api/weather/", views.get_weather_info, name="get_weather_info"),
    
]
