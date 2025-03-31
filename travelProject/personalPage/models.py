from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class TravelPlan(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} by {self.created_by.username}"

class Destination(models.Model):
    travel_plan = models.ForeignKey(TravelPlan, related_name='destinations', on_delete=models.CASCADE)
    place = models.CharField(max_length=100)  # 地點
    date = models.CharField(max_length=100)  # 前往日期

    def __str__(self):
        return f"{self.place} on {self.date}"