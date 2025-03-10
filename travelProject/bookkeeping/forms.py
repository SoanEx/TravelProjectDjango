from django import forms
from bookkeeping.models import Record

class RecordForm(forms.ModelForm):
    
    class Meta:
        model = Record
        fields = ("created_by","date","types","amount","note")

