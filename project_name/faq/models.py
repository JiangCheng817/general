from django.db import models


# 常见问题
from project_name.enduser.models import EndUser


class Support(models.Model):
    """
    常见问题(用户帮助)
    """
    id = models.AutoField(primary_key=True)
    question = models.CharField(max_length=30, verbose_name="help question")
    answer = models.TextField(verbose_name="help answer")
    type = models.CharField(max_length=50, null=True, blank=True, verbose_name="help type")
    delete_flag = models.SmallIntegerField(default=0, verbose_name="delete flag")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="create time")
    update_time = models.DateTimeField(auto_now=True, verbose_name="update time")

    class Meta:
        db_table = "support"

    def __str__(self):
        return self.question[:10]


# 用户反馈基类
class FeedbackBase(models.Model):
    """
    feedback（意见反馈）
    """
    FEEDBACK_HANDLE_STATUS=(
        (1, "has been handled"),
        (2, "hasn't been handled")
    )
    id = models.AutoField(primary_key=True)
    content = models.TextField(blank=True, null=True, verbose_name="faq content")
    image = models.CharField(blank=True, null=True, verbose_name="image", max_length=150)
    status = models.SmallIntegerField(choices=FEEDBACK_HANDLE_STATUS, default=2, verbose_name="status")
    delete_flag = models.SmallIntegerField(default=0, verbose_name="delete flag")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="create time")
    update_time = models.DateTimeField(auto_now=True, verbose_name="update time")

    class Meta:
        db_table = "feedback_base"
        abstract = True


# 用户反馈简单举例
class Feedback(FeedbackBase):
    # @字段需补充完整
    # 一个简单的例子
    user = models.ForeignKey(EndUser, on_delete=models.CASCADE, db_column="enduser_id", verbose_name="create_user")

    class Meta:
        db_table = "feedback"