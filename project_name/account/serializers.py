# -*- coding:utf-8 -*-
#!/usr/bin/env python
# xiaoz
import re

from rest_framework import serializers

from project_name.account.models import User


class CaptchaSerializer(serializers.Serializer):
    captcha = serializers.CharField(min_length=6, read_only=True)
    # c_type 用于标识此验证码用于什么场景
    c_type = serializers.IntegerField(default=0)
    account = serializers.CharField(max_length=40)
    app_id = serializers.CharField(max_length=32, required=False)

    def validate(self, attrs):
        account = attrs['account']
        c_type = attrs['c_type']
        app_id = attrs['app_id']
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