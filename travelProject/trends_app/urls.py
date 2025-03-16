from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('fetch/', views.fetch_data_view, name='fetch_data'),
    path('train/', views.train_model_view, name='train_model'),
    path('predict/', views.predict_view, name='predict'),
]
