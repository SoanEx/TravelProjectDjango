import datetime
from django.shortcuts import render,redirect
from django.views import View
from bookkeeping.models import Record,MemberRelation
from bookkeeping.forms import RecordForm
from django.contrib.auth.models import User
from django.db.models import Sum
# Create your views here.

def newitem(request):
    fm = RecordForm(request.POST or None)
    memberlist = User.objects.all()
     # memberlist = User.objects.filter(group__name="")
    if request.method == "POST":
        if fm.is_valid():
            fm_info = fm.save()
            inserted_id = fm_info.id
            vlist = request.POST.getlist('membercheckbox',[])
            for v in vlist:
                MemberRelation.objects.create(
                    no_id = inserted_id,
                    member = v,
                    types = request.POST.get('types'),
                    avg = (float(request.POST.get('amount'))/len(vlist))) 
           
            return redirect('/items') 
    else:
        return render(request, 'bookkeeping/newitem.html', {'form': fm,'member_list':memberlist})

class Items(View):
    def get(self, request):
        itemslist = Record.objects.all()
        totals = 0
        for item in itemslist:
            totals += item.amount
        selectlist = MemberRelation.objects.all()
        return render(request,"bookkeeping/items.html",{"items_list":itemslist,"select_list":selectlist,"total":totals})
    
class DelItem(View):
    def post(self, request):
        id = request.POST.get('id')
        delet_item = Record.objects.get(id=id)
        delet_item.delete()
        return redirect("/items")

class Details(View):
    def get(self, request):
        selectlist = MemberRelation.objects.values_list("member",flat=True)
        userlist = User.objects.filter(username__in=selectlist).values_list("username",flat=True)
        relationlist =  MemberRelation.objects.values('member','types').annotate(total = Sum('avg'))
        itemslist = Record.objects.all()
        return render(request,"bookkeeping/details.html",{"user_list":userlist,"relation_list":relationlist,"items_list":itemslist}) 

def index(request):
    return render(request,"bookkeeping/index.html")