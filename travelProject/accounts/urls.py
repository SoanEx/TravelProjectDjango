# travelProject/accounts/urls.py

# accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.registration_login, name='registration_login'),
    path('check_username/', views.check_username, name='check_username'),
    path('google_auth_verify/', views.google_auth_verify, name='google_auth_verify'),
    path('test_twilio/', views.test_twilio, name='test_twilio'),  
    path('accounts/google_redirect/callback/', views.google_redirect_callback, name='google_redirect_callback'),
    path('search-user/', views.search_user_view, name='search_user'),
]
