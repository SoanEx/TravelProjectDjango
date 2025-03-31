from django.urls import path
from . import views

urlpatterns = [
    path('', views.personal_page, name='personal_page'),
    path('create-travel/', views.create_travel_plan, name='create_travel_plan'),
    path('travel/<int:pk>/', views.travel_plan_detail, name='travel_plan_detail'),
    path('travel-plan/<int:pk>/edit/', views.edit_travel_plan, name='edit_travel_plan'),
]