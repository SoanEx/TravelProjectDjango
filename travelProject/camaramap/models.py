from django.db import models

# Create your models here.
# class SpeedCamera(models.Model):
#     latitude = models.FloatField()
#     longitude = models.FloatField()
#     location = models.CharField(max_length=255)

class Attraction(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    description = models.TextField()