# forms.py
from django import forms
from bookkeeping.models import Record

class RecordForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = ['date', 'types', 'amount', 'note']  # created_by可手動指定
        widgets = {
            'date': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            )
        }
