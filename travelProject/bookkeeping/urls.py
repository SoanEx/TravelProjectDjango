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

from django.urls import path
from . import views


urlpatterns = [
    path('index/',views.index,name="index"),
    path("details/",views.Details.as_view(),name="details"),
    path("items/",views.Items.as_view(),name="items"),
    path("del-item",views.DelItem.as_view(),name="del-item"),
    path("newitem/",views.newitem,name="newitem"),
    path('search_member_api/',views.search_member_api, name='search_member_api'),
]
