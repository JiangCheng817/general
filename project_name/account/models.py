import binascii
import os
from datetime import datetime,timedelta

from django.contrib.auth.models import AbstractUser, UserManager, PermissionsMixin
from django.db import models


# user
from project_name.config import settings


class User(AbstractUser):

    """
    # Web User Table
    """

    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=64, unique=True, verbose_name="username")
    cellphone = models.CharField(max_length=16, null=False, blank=True, verbose_name="cellphone")
    email = models.CharField(max_length=50, null=True, blank=True, verbose_name="email")
    is_active = models.BooleanField(default=True, verbose_name="is active")
    is_admin = models.BooleanField(default=False, verbose_name="is admin")
    is_staff = models.BooleanField(default=True, verbose_name="is staff")
    is_superuser = models.BooleanField(default=False, verbose_name="is superuser")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="updated at")

    class Meta:
        db_table = 'account_user'
        unique_together = ('cellphone', 'email')

    def __str__(self):
        return self.username

    # 这两个方法必须实现,但是这里都直接返回username
    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        return self.username

    def get_short_name(self):
        """
        "Returns the short name for the user."
        """
        return self.username


class Captcha(models.Model):
    TYPE_CHOICE = (
        ('0', "web"),
        ('1', "app"),
        ('2', "device")
    )
    captcha = models.CharField(max_length=6)
    c_type = models.CharField(max_length=1, verbose_name="captcha type", choices=TYPE_CHOICE)
    # 默认手机号
    account = models.CharField(max_length=16, blank=True, null=True)
    app_id = models.CharField(max_length=32, blank=True, null=True)
    create_at = models.DateTimeField(auto_now_add=True)
    expire_at = models.DateTimeField()

    class Meta:
        db_table = 'captcha'


class WebToken(models.Model):
    """
        The customize authorization token model.
    """
    access_token = models.CharField(max_length=40)
    refresh_token = models.CharField(max_length=40)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='web_user_token',
        on_delete=models.CASCADE
    )
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.access_token:
            self.access_token = self.generate_key()
            self.refresh_token = self.generate_key()
        return super(WebToken, self).save(*args, **kwargs)

    def refresh(self):
        self.access_token = self.generate_key()
        self.created = datetime.now()
        self.save(update_fields=['access_token', 'refresh_token', 'created'])

    def at_is_expired(self):
        return datetime.now() > self.created+timedelta(hours=1)

    def rt_is_expired(self):
        return datetime.now() > self.created+timedelta(hours=6)

    @staticmethod
    def generate_key():
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.access_token
