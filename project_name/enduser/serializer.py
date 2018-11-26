# -*- coding:utf-8 -*-
#!/usr/bin/env python
# xiaoz
from datetime import datetime

from django.db.models import Q
from rest_framework import serializers

from project_name.account.models import Captcha
from project_name.app.models import App
from project_name.core.util.generator import gen_enduser_id
from project_name.enduser.models import EndUser


class SignupSerializer(serializers.Serializer):
    enduser_id = serializers.CharField(read_only=True)
    account = serializers.CharField()
    password = serializers.CharField(min_length=8)
    app_id = serializers.CharField()
    captcha = serializers.CharField(max_length=6)

    def validate(self, attrs):
        account = attrs['account']
        captcha = attrs['captcha']
        if EndUser.objects.filter(Q(cellphone=account)|Q(email=account)):
            raise serializers.ValidationError('account has been registered')
        try:
            captcha = Captcha.objects.get(captcha=captcha, account=account, c_type=1)
            if captcha.expire_at < datetime.now():
                raise serializers.ValidationError('captcha has been expired')
        except captcha.DoesNotExist:
            raise serializers.ValidationError('captcha does not exist')
        return attrs

    def create(self, validated_data):
        password = validated_data['password']
        enduser_id = gen_enduser_id()
        account = validated_data['account']
        cellphone = account if account.isdigit() else None
        email = account if account.count('@')==1 else None
        app_id = validated_data['app_id']
        try:
            app = App.objects.get(app_id=app_id, is_delete=False)
        except App.DoesNotExist:
            raise serializers.ValidationError('app_id error')

        try:
            enduser = EndUser.objects.create(
                enduser_id=enduser_id,
                cellphone=cellphone,
                email=email,
                app=app
            )
        except Exception as e:
            raise serializers.ValidationError(repr(e))
        enduser.set_password(password)
        enduser.save()
        return enduser

