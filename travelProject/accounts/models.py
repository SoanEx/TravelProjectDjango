from django.db import models

# Create your models here.
# accounts/models.py

from django.contrib.auth.models import User
from django.core.validators import RegexValidator



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # 手機號碼，使用 E.164 格式（例如 +886912345678）
    phone_number = models.CharField(
        max_length=20,
        unique=False,
        validators=[
            RegexValidator(
                regex=r'^\+\d{10,15}$',
                message="請以 E.164 格式輸入手機號碼，例如 +886912345678"
            )
        ],
        blank=True
    )

    def __str__(self):
        return f"{self.user.username}'s profile"
    
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

