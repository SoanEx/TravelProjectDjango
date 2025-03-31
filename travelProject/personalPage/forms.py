from django import forms
from .models import TravelPlan, Destination

class TravelPlanForm(forms.ModelForm):
    class Meta:
        model = TravelPlan
        fields = ['title', 'description', 'budget']

class DestinationForm(forms.ModelForm):
    class Meta:
        model = Destination
        fields = ['place', 'date']