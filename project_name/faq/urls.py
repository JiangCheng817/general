# -*- coding:utf-8 -*-
# !/usr/bin/env python
# xiaoz
from django.conf.urls import url


from . import views

urlpatterns = [
    url(r'^support/', views.SupportView.as_view(), name='support'),
    url(r'^feedback/', views.FeedbackView.as_view(), name='feedback'),

]