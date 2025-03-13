from django.shortcuts import render

def personal_page(request):
    return render(request, "personalPage.html")