from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from .models import TravelPlan, Destination
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.views.generic import ListView
from .models import TravelPlan
import uuid

# 創建訪客用戶
def create_guest_user(request):
    if not request.session.get('guest_user_id'):
        random_username = f"guest_{uuid.uuid4().hex[:8]}"
        user = User.objects.create_user(username=random_username, password=None)
        # (如果有自訂 Profile）
        # user.profile.is_guest = True
        # user.profile.save()

        # 將用戶保存到 session 中
        request.session['guest_user_id'] = user.id
        login(request, user)
    else:
        # 從 session 中獲取用戶
        user = User.objects.get(id=request.session['guest_user_id'])
    return user


def create_travel_plan(request):
    if not request.user.is_authenticated:
        user = create_guest_user(request)
    else:
        user = request.user

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        budget = request.POST.get('budget')

        # 建立旅行計畫
        travel_plan = TravelPlan.objects.create(
            created_by=user,  # 修正為 user
            title=title,
            description=description,
            budget=budget
        )

        # 手動取得目的地資料
        places = request.POST.getlist('places[]')
        dates = request.POST.getlist('dates[]')

        # 確保至少有一組目的地資料
        for place, date in zip(places, dates):
            if place and date:
                Destination.objects.create(
                    travel_plan=travel_plan,
                    place=place,
                    date=date
                )

        return redirect('personal_page')

    return render(request, 'react/create_travel_plan.html')
    
def edit_travel_plan(request, pk):
    travel_plan = get_object_or_404(TravelPlan, pk=pk)

    if request.method == 'POST':
        # 更新 TravelPlan
        travel_plan.title = request.POST.get('title')
        travel_plan.description = request.POST.get('description')
        travel_plan.budget = request.POST.get('budget')
        travel_plan.save()

        # 取得目的地資料
        places = request.POST.getlist('places[]')
        dates = request.POST.getlist('dates[]')

        # 先刪除舊的目的地資料，然後重新建立
        travel_plan.destinations.all().delete()

        for place, date in zip(places, dates):
            if place and date:
                Destination.objects.create(
                    travel_plan=travel_plan,
                    place=place,
                    date=date
                )

        return redirect('travel_plan_detail', pk=travel_plan.pk)

    destinations = travel_plan.destinations.all()

    return render(request, 'react/edit_travel_plan.html', {'travel_plan': travel_plan, 'destinations': destinations})



def personal_page(request):
    if not request.user.is_authenticated:
        user = create_guest_user(request)
    else:
        user = request.user

    # 取得該使用者建立的所有旅遊計畫
    travel_plans = TravelPlan.objects.filter(created_by=request.user)
    return render(request, 'react/index.html', {'travel_plans': travel_plans}) 

class TravelPlanListView(ListView):
    model = TravelPlan
    template_name = 'personalPage/travel_plan_list.html'
    context_object_name = 'travel_plans'

    def get_queryset(self):
        # 僅顯示當前使用者創建的計畫
        return TravelPlan.objects.filter(created_by=self.request.user)


def travel_plan_detail(request, pk):
    travel_plan = get_object_or_404(TravelPlan, pk=pk)
    destinations = Destination.objects.filter(travel_plan=travel_plan)
    return render(request, 'react/travel_plan_detail.html', {'travel_plan': travel_plan, 'destinations': destinations})