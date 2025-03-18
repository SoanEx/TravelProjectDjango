from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Record(models.Model):
    created_by = models.ForeignKey(User,on_delete=models.CASCADE)
    date = models.CharField(max_length=60)
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
    no_id = models.IntegerField()
    member = models.CharField(max_length=255)
    avg = models.FloatField(default=0)
    types = models.CharField(max_length=20)