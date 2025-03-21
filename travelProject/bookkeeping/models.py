from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Record(models.Model):
    created_by = models.ForeignKey(User,on_delete=models.CASCADE)
    date = models.DateField()
    type_choiches=[
        ('food','food'),
        ('transport','transport'),
        ('accommodation','accommodation'),
        ('tickets','tickets'),
        ('others','others')
        ]
    types = models.CharField(max_length=20,choices=type_choiches,default='food')
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    note = models.CharField(max_length=255,blank=True)
    
class MemberRelation(models.Model):
    record = models.ForeignKey(Record, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    member = models.CharField(max_length=255)
    avg = models.FloatField(default=0)
    types = models.CharField(max_length=20)