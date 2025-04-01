from django.shortcuts import render

# Create your views here.
# funstuff/views.py
from .forms import ExplosiveQuizForm

from .forms import FeedbackForm  # 你自訂的四選一表單

def feedback_explosive_view_PHYSICS(request):
    """
    這個 View 示範使用 Matter.js 做「真實物理爆炸」，
    而不是傳統 CSS/Anime.js 動畫。
    """
    form = FeedbackForm()
    
    # 你可以根據需求決定是否需要在後端處理 POST
    # 如果不需要，就單純帶一個 form 給前端
    # example: check if request.method == 'POST': ...
    
    # 爆炸文字可自訂，也可來自 DB / form 
    explosion_text = "設計者:林瀚群、古景睿、鄭仲軒、陳宣伊"
    
    context = {
        'user': request.user,        # 假設你想在模板顯示使用者
        'form': form,
        'explosion_text': explosion_text
    }
    return render(request, 'funstuff/widgets/feedback_explosive_physics.html', context)

def feedback_explosive_view(request):
    correct_answer = False       # 用來判斷是否觸發爆炸
    explosion_text = "Boom！這是個非常「不好」的回答？"  # 你想顯示的爆炸文字

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            user_choice = form.cleaned_data['feedback_choice']
            # 假設 "D" 表示「非常不好」
            if user_choice == 'D':
                correct_answer = True
    else:
        form = FeedbackForm()

    context = {
        'user': request.user,
        'form': form,
        'correct_answer': correct_answer,
        'explosion_text': explosion_text,
    }
    return render(request, 'funstuff/widgets/feedback_explosive.html', context)

def explosive_quiz_view(request):
    """
    這個 view 負責顯示並處理 "爆炸表單"
    其他 app 只要在 URL 連結到這個 view，即可使用。
    """
    correct_answer = False
    explosion_text = "Boom！恭喜你答對了！"

    if request.method == 'POST':
        form = ExplosiveQuizForm(request.POST)
        if form.is_valid():
            user_answer = form.cleaned_data['answer']
            # 假設正確答案是 'C'
            if user_answer == 'C':
                correct_answer = True
    else:
        form = ExplosiveQuizForm()

    context = {
        'form': form,
        'correct_answer': correct_answer,
        'explosion_text': explosion_text,
    }

    # 這裡直接渲染 "funstuff/widgets/explosive_quiz.html"
    # 也可改成自己的獨立模板
    return render(request, 'funstuff/widgets/explosive_quiz.html', context)
