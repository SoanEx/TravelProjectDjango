# funstuff/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('quiz/', views.explosive_quiz_view, name='explosive_quiz'),
    path('feedback/', views.feedback_explosive_view, name='feedback_explosive'),
    path('feedback/physics/', views.feedback_explosive_view_PHYSICS, name='feedback_explosive_physics'),
]

