# models.py

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
import json

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # 手機號碼，使用 E.164 格式（例如 +886912345678），採用 RegexValidator
    phone_number = models.CharField(
        max_length=20,
        unique=False,
        validators=[
            RegexValidator(
                regex=r'^\+\d{10,15}$',
                message="請以 E.164 格式輸入手機號碼，例如 +886912345678"
            )
        ],
        blank=True,
        null=True
    )
    phone_verified = models.BooleanField(default=False)
    # 用來存已驗證通過的 device_id 清單，示範直接用 TextField 存 JSON
    known_devices = models.TextField(default='[]')

    def __str__(self):
        return f"{self.user.username}'s profile"

    def get_known_devices(self):
        try:
            return json.loads(self.known_devices)
        except:
            return []

    def add_known_device(self, device_id):
        devices = self.get_known_devices()
        if device_id not in devices:
            devices.append(device_id)
            self.known_devices = json.dumps(devices)
            self.save()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
