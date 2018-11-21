from django.contrib.auth.models import AbstractUser, UserManager, PermissionsMixin
from django.db import models


# user
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
    captcha = models.CharField(max_length=6)
    c_type = models.IntegerField(verbose_name="captcha type")
    # 默认手机号
    account = models.CharField(max_length=16, verbose_name="cellphone")
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
