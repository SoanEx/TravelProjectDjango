from django.contrib import admin
from .models import TravelPlan, Destination  # 正確匯入模型

# Register your models here.
admin.site.register(TravelPlan)
admin.site.register(Destination)