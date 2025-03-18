from django.shortcuts import render

def personal_page(request):
    return render(request, "react/personalPage.html")  # 渲染 React 編譯後的 index.html