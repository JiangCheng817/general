# -*- coding:utf-8 -*-
# !/usr/bin/env python
# xiaoz
from django.conf.urls import url


from . import views

urlpatterns = [
    url(r'^supports/', views.SupportsView.as_view(), name='supports'),
    url(r'^support/(?P<support_id>[0-9]+)', views.SupportView.as_view(), name='support'),

]