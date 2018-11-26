from django.contrib.postgres.fields import JSONField
from django.db import models

# Create your models here.
from project_name.account.models import User


class App(models.Model):
    APP_STATUS_CHOICES = (
        (0, '开发中'),
        (1, '审核中'),
        (2, '已上线'),
    )

    app_id = models.CharField(primary_key=True, max_length=36, verbose_name="AppID")
    status = models.IntegerField(choices=APP_STATUS_CHOICES, default=0)
    name = models.CharField(max_length=64, verbose_name="应用名称")
    e_name = models.CharField(max_length=64, null=True, blank=True, verbose_name="英文名称")
    description = models.CharField(max_length=1024, verbose_name="应用描述")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=u"生产厂家")
    iot_key = models.CharField(max_length=64, verbose_name='阿里productKey')
    is_delete = models.BooleanField(default=False, verbose_name=u"逻辑删除标志")
    extra = JSONField(default=dict, null=True, blank=True, verbose_name="extra fields")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="create time")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="update time")

    class Meta:
        db_table = 'app'
        ordering = ("-created_at",)

    def __str__(self):
        return self.name