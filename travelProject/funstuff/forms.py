# funstuff/forms.py
from django import forms

class ExplosiveQuizForm(forms.Form):
    """
    四選一的簡單表單，用於示範答對後爆炸特效
    """
    CHOICES = [
        ('A', '選項 A'),
        ('B', '選項 B'),
        ('C', '選項 C'),
        ('D', '選項 D'),
    ]
    answer = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)


class FeedbackForm(forms.Form):
    FEEDBACK_CHOICES = [
        ('A', '非常好'),
        ('B', '還不錯'),
        ('C', '普通'),
        ('D', '非常不好'),
    ]
    feedback_choice = forms.ChoiceField(
        choices=FEEDBACK_CHOICES,
        widget=forms.RadioSelect
    )