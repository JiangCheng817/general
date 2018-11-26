from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.postgres.fields import JSONField
from django.db import models


# 终端用户
from project_name.app.models import App


class EndUser(AbstractBaseUser):
    enduser_id = models.CharField(primary_key=True, max_length=32, verbose_name=u'终端用户UID')
    app = models.ForeignKey(App, on_delete=models.CASCADE, db_column="app_id", verbose_name="application")
    cellphone = models.CharField(max_length=20, blank=True, null=True, verbose_name=u'手机号码')
    phone_area = models.CharField(max_length=10, blank=True, null=True, default='+86', verbose_name=u'归属地')
    email = models.EmailField(max_length=256, blank=True, null=True, verbose_name=u'邮箱')
    nick_name = models.CharField(max_length=40, blank=True, null=True, verbose_name=u'昵称')
    name = models.CharField(max_length=40, blank=True, null=True, verbose_name=u'姓名')
    gender = models.CharField(max_length=10, blank=True, null=True, verbose_name=u'性别')
    city = models.CharField(max_length=40, blank=True, null=True, verbose_name=u'所在城市')
    avatar = models.CharField(max_length=512, blank=True, null=True, verbose_name=u'头像')
    note = models.CharField(max_length=256, blank=True, null=True, verbose_name=u'备注')
    is_active = models.BooleanField(u'is activation', default=True)
    is_virtual = models.BooleanField(u'是否虚拟', default=False)
    is_online = models.BooleanField(u'在线状态', default=False)
    is_delete = models.BooleanField(default=False, verbose_name="is delete")
    iot_secret = models.CharField(max_length=50, verbose_name=u"IOT秘钥")
    online_times = models.IntegerField(default=0, verbose_name=u"上线次数")
    extra = JSONField(default=dict, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    REQUIRED_FIELDS = ['cellphone', 'name']
    USERNAME_FIELD = 'cellphone'

    class Meta:
        db_table = 'enduser'
        unique_together = ("app", "cellphone")

    def __str__(self):
        return self.cellphone if self.cellphone else self.email

    def get_full_name(self):
        return self.name