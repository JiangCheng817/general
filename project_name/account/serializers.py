# -*- coding:utf-8 -*-
#!/usr/bin/env python
# xiaoz
import re
from datetime import datetime

from django.db.models import Q
from rest_framework import serializers

from project_name.account.models import User, Captcha


class CaptchaSerializer(serializers.Serializer):
    # c_type 用于标识此验证码用于什么场景
    c_type = serializers.IntegerField(default=0)
    account = serializers.CharField(max_length=40)
    app_id = serializers.CharField(max_length=32, required=False)

    def validate(self, attrs):
        account = attrs['account']
        c_type = attrs['c_type']
        # app_id = attrs['app_id']

        if c_type not in (0, 1, 2):
            raise serializers.ValidationError("Captcha type must be 0 or 1 or 2")
        if account.count("@") == 1:
            email_re = re.compile(r'^[A-Za-z0-9\u4e00-\u9fa5]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$')
            if not email_re.match(account):
                raise serializers.ValidationError("Email format is invalid")
        elif account.isdigit():
            cellphone_re = re.compile(r'^(1[34578]\d{9})$')
            if not cellphone_re.match(account):
                raise serializers.ValidationError("Cellphone format is invalid")
        else:
            raise serializers.ValidationError("account must be a cellphone or email,you may spell it wrong")
        # 检验是否存在app @todo
        return attrs


class SignupSerializer(serializers.Serializer):
    account = serializers.CharField()
    username = serializers.CharField()
    password = serializers.CharField(min_length=8)
    password_2 = serializers.CharField(min_length=8)
    captcha = serializers.CharField()

    class Meta:
        fields = ("username", "account", "password", "password_2", "captcha")

    def validate(self, attrs):
        account = attrs['account']
        password = attrs['password']
        password_2 = attrs['password_2']
        captcha = attrs['captcha']
        username = attrs['username']
        if password != password_2:
            raise serializers.ValidationError("password you enter twice is not consistence")
        if User.objects.filter(Q(cellphone=account)|Q(email=account)).exists():
            raise serializers.ValidationError("account has already been register")
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("This name has been used")
        # account 默认为手机号
        try:
            captcha = Captcha.objects.get(captcha=captcha, account=account)
        except Captcha.DoesNotExist:
            raise serializers.ValidationError("Captcha error")
        else:
            if captcha.expire_at < datetime.now():
                raise serializers.ValidationError("Captcha expired")
        return attrs

    def create(self, validated_data):
        username = validated_data['username']
        account = validated_data['account']
        cellphone = account if account.isdigit() else None
        email = account if account.count('@') == 1 else None
        password = validated_data['password']
        try:
            user = User.objects.create(
                username=username,
                cellphone=cellphone,
                email=email
            )
        except Exception as e:
            raise serializers.ValidationError(repr(e))
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=8)
    username = serializers.CharField()

    class Meta:
        fields = ('password', 'username')


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=8)
    new_password = serializers.CharField(min_length=8)


class ForgetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=8)
    captcha = serializers.CharField(max_length=6)
    cellphone = serializers.CharField()

    def validate(self, attrs):
        cellphone = attrs['cellphone']
        captcha = attrs['captcha']
        try:
            User.objects.get(cellphone=cellphone)
        except User.DoesNotExist:
            raise serializers.ValidationError('user does not exist')
        try:
            captcha = Captcha.objects.get(captcha=captcha, account=cellphone, c_type=0)
            if captcha.expire_at < datetime.now():
                raise serializers.ValidationError('captcha expired')
        except Captcha.DoesNotExist:
            raise serializers.ValidationError('captcha error')
        return attrs


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("username", "cellphone", "email", "is_active", "is_admin", "is_superuser", "created_at", "id")