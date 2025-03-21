from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from accounts.models import Profile
from datetime import timedelta

class Command(BaseCommand):
# 如何執行
# 
# 在專案根目錄 (同層有 manage.py) 下敲指令：
# 
#     python manage.py cleanup_guests --days=14
# 
# 代表刪除「14天未使用」的 guest 帳號。
# 若不加 --days，則預設是 7 天：
# 
#     python manage.py cleanup_guests
# 
# 若你想要定期自動執行，可用 Linux crontab、Windows Task Scheduler 或 Celery Beat 等排程。

    help = '清理超過 N 天未使用的 Guest 帳號'

    def add_arguments(self, parser):
        """
        可在指令後使用 --days 參數指定清理天數，如:
        python manage.py cleanup_guests --days=7
        """
        parser.add_argument('--days', type=int, default=7, help='天數，預設7天')

    def handle(self, *args, **options):
        days = options['days']
        threshold = timezone.now() - timedelta(days=days)

        # 篩選「is_guest = True」 且 「last_login < threshold」的 Profile
        old_guest_profiles = Profile.objects.filter(
            is_guest=True,
            user__last_login__lt=threshold
        )

        count = old_guest_profiles.count()
        if count == 0:
            self.stdout.write(self.style.WARNING("沒有符合清理的 guest 帳號"))
            return

        # 根據這些 profile, 刪除對應 User
        User.objects.filter(profile__in=old_guest_profiles).delete()

        self.stdout.write(self.style.SUCCESS(
            f"已刪除 {count} 個 Guest 帳號 (超過 {days} 天未使用)"
        ))
