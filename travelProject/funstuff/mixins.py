# funstuff/mixins.py
import random
import string

class FunMixin:
    """
    這個 Mixin 可以用在其他 app 的 class-based view 之中，
    提供一些「有趣」或「隨機」的功能。
    """
    def get_fun_string(self, length=8):
        """回傳一個指定長度的隨機字串"""
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
