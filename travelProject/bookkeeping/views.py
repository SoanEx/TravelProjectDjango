from django.shortcuts import render,redirect
from django.views import View
from bookkeeping.models import Record,MemberRelation
from bookkeeping.forms import RecordForm
from django.contrib.auth.models import User
from django.db.models import Sum
import uuid
from django.contrib.auth import login
from django.http import JsonResponse
from django.db.models import Q
# Create your views here.                       

def create_guest_user():
    random_username = f"guest_{uuid.uuid4().hex[:8]}"
    user = User.objects.create_user(username=random_username, password=None)
    # 若你有 Profile 並已新增 is_guest 欄位，則：
    user.profile.is_guest = True
    user.profile.save()
    return user

def newitem(request):
    # 確保登入者(guest or real user)
    if not request.user.is_authenticated:
        guest_user = create_guest_user()
        guest_user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, guest_user)

    fm = RecordForm(request.POST or None)
    # 預設顯示的 member_list
    # (如果你想一開始就顯示全部，或顯示空list都可以)
    memberlist = User.objects.filter(is_staff=False, is_superuser=False, is_active=True)

    if request.method == "POST":
        if fm.is_valid():
            record = fm.save(commit=False)
            record.created_by = request.user
            record.save()
            
            vlist = request.POST.getlist('membercheckbox', [])
            for v in vlist:
                MemberRelation.objects.create(
                    record=record,
                    created_by=record.created_by,
                    member=v,
                    types=record.types,
                    avg=(float(request.POST.get('amount')) / len(vlist)) if vlist else 0
                )

            # 建立完紀錄 => redirect
            return redirect('/bk/items')
    else:
        # GET - 顯示表單
        pass
    
    return render(request, 'bookkeeping/newitem.html', {
        'form': fm,
        'member_list': memberlist
    })



class Items(View):
    def get(self, request):
        if not request.user.is_authenticated:
            # 未登入時要跳轉登入或顯示訊息(視情況需求)
            return redirect('/accounts/login')

        # 只撈「目前登入使用者」建立的紀錄
        itemslist = Record.objects.filter(created_by=request.user)
        
        # 如果也要統計只屬於該使用者的資料
        type_amount = itemslist.values('types').annotate(total=Sum('amount'))

        expensedata = []
        for j in type_amount:
            expensedata.append({ "y": float(j["total"]), "name": j['types'] })

        # 計算總和
        totals = 0
        for item in itemslist:
            totals += item.amount

        # 如果你想要顯示該使用者相關的 MemberRelation，可根據需求再過濾
        # 例如若只想顯示「該使用者本人建立的」：
        selectlist = MemberRelation.objects.filter(created_id=request.user.id)

        return render(request, "bookkeeping/items.html", {
            "items_list": itemslist,
            "select_list": selectlist,
            "total": totals,
            "expense_data": expensedata
        })


class DelItem(View):
    def post(self, request):
        record_id = request.POST.get('id')
        
        # 情況1: 沒帶 id 或 id 是空字串
        if not record_id:
            # 你可以選擇顯示錯誤訊息 / 或直接跳轉
            return redirect("/bk/items")

        try:
            delet_item = Record.objects.get(id=record_id)
        except Record.DoesNotExist:
            # 情況2: 該 id 不存在於資料庫
            # 同樣地，你可以顯示提示/記錄log/或直接跳轉
            return redirect("/bk/items")

        # 如果成功找到該 record，就執行刪除
        MemberRelation.objects.filter(record=delet_item).delete()
        delet_item.delete()
        return redirect("/bk/items")


class Details(View):
    def get(self, request):
        selectlist = MemberRelation.objects.values_list("member",flat=True)
        userlist = User.objects.filter(username__in=selectlist).values_list("username",flat=True)
        relationlist =  MemberRelation.objects.values('member','types').annotate(total = Sum('avg'))
        usersumlist =  MemberRelation.objects.values('member').annotate(total = Sum('avg'))
        return render(request,"bookkeeping/details.html",{"user_list":userlist,"relation_list":relationlist,"usersum_list":usersumlist}) 

def index(request):
    return render(request,"bookkeeping/index.html")

def search_member_api(request):
    keyword = request.GET.get('keyword', '').strip()
    # 篩選非 staff, superuser
    queryset = User.objects.filter(is_staff=False, is_superuser=False, is_active=True)

    if keyword:
        queryset = queryset.filter(
            Q(username__icontains=keyword) | Q(profile__phone_number__icontains=keyword)
        )
    
    # 回傳資料，通常只需要 id, username
    results = []
    for user in queryset:
        results.append({
            'id': user.id,
            'username': user.username,
        })
    
    return JsonResponse({'members': results})