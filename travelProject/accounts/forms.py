# accounts/forms.py
from django import forms
from django.contrib.auth.models import User

class RegistrationForm(forms.ModelForm):
    email = forms.EmailField(required=True, label="電子郵件")
    password = forms.CharField(widget=forms.PasswordInput, min_length=8, label="密碼")
    confirm_password = forms.CharField(widget=forms.PasswordInput, min_length=8, label="確認密碼")
    phone_local = forms.CharField(required=True, label="手機號碼", help_text="例如 0912345678")
    country = forms.ChoiceField(
        choices=(
            ('TW', '台灣 (+886)'),
            ('US', '美國 (+1)'),
            # 可再加其他國家
        ),
        label="國家"
    )
    
    class Meta:
        model = User
        # 假設你將 email 當作 username 來源，所以只讓使用者輸入 email
        fields = ['email']
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "密碼與確認密碼不一致")
        return cleaned_data

    def save(self, commit=True):
        # 將 email 的 @ 前面部分當作 username，並記錄 email
        user = super().save(commit=False)
        email = self.cleaned_data["email"]
        username = email.split('@')[0]  # @ 前面的部分
        user.username = username
        user.email = email  # 儲存完整信箱
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

# accounts/forms.py
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class RegistrationLoginForm(forms.Form):
    username = forms.EmailField(required=True, label="帳號 (Email)")
    password = forms.CharField(required=True, widget=forms.PasswordInput, label="密碼")
    confirm_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput,
        label="確認密碼"
    )
    country = forms.ChoiceField(
        choices=(
            ('TW', '台灣 (+886)'),
            ('US', '美國 (+1)'),
        ),
        required=True,
        label="國家"
    )
    phone_local = forms.CharField(
        required=True,
        label="手機號碼"
    )

    def __init__(self, user_exists=False, *args, **kwargs):
        """
        user_exists: 用來區分「帳號已存在 → 登入」或「帳號不存在 → 註冊」.
        """
        self.user_exists = user_exists
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        # 若帳號不存在 → 需要確認密碼
        if not self.user_exists:
            if not confirm_password:
                raise ValidationError("請輸入確認密碼")
            if password != confirm_password:
                self.add_error('confirm_password', "密碼與確認密碼不一致")

        return cleaned_data
