from django.db import models

class TrendData(models.Model):
    keyword = models.CharField(max_length=100)
    date = models.DateField()
    interest = models.IntegerField()  # 0~100

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.keyword} - {self.date}: {self.interest}"
