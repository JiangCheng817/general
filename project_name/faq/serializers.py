# -*- coding:utf-8 -*-
#!/usr/bin/env python
# xiaoz
from rest_framework import serializers

from .models import Support, Feedback, FeedbackBase


class SupportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Support
        fields = ("id", "question", "answer", "type", "create_time")


# 用户反馈序列化类基类
class FeedbackBasicSerializer(serializers.ModelSerializer):
    image = serializers.CharField(required=False)
    content = serializers.CharField(required=False)

    class Meta:
        model = FeedbackBase


class FeedbackSerializer(FeedbackBasicSerializer):
    user = serializers.CharField(required=False, read_only=True)

    class Meta:
        model = Feedback

    def create(self, validated_data):
        user = self.context["user"]
        image = self.context["image"] or None
        validated_data.update({
            "user": user,
            "image": image
        })
        instance = super(FeedbackSerializer, self).create(validated_data)
        return instance