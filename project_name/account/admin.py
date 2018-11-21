from django.contrib import admin

# Register your models here.
from project_name.account.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "created_at")


admin.site.register(User, UserAdmin)
