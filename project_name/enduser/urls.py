# -*- coding:utf-8 -*-
#!/usr/bin/env python
# xiaoz
from django.conf.urls import url

from project_name.enduser import views

urlpatterns = [

    # url(r'^login/', views.LoginView.as_view(), name='login'),
    url(r'^signup/', views.SignupView.as_view(), name='signup'),
    #
    # url(r'^refresh/token/', views.RefreshTokenView.as_view(), name='refresh token'),
    # url(r'^password/', views.PasswordView.as_view(), name="password"),
    # url(r'^logout/', views.LogoutView.as_view(), name='logout'),
    # url(r'^forget/password/', views.ForgetPasswordView.as_view(), name='forget password'),
    # url(r'^user/info/',views.UserView.as_view(), name='user info')
]