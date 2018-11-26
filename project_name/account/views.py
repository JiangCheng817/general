from datetime import datetime, timedelta

# Create your views here.
from django.contrib.auth import logout
from rest_framework.views import APIView
from rest_framework import permissions

from project_name.account.models import Captcha, User
from project_name.core import error_code
from project_name.core.authentication import TokenAuthentication
from project_name.core.util.generator import captcha_generator
from project_name.core.util.redis_relate import set_access_token, set_refresh_token, ACCESS_TOKEN_EXPIRED_TIME, \
    get_refresh_token, delete_token
from project_name.utils.custom_exception import ServerError
from project_name.utils.custom_response import simple_response
from .serializers import CaptchaSerializer, SignupSerializer, LoginSerializer, RefreshTokenSerializer, \
    PasswordSerializer, ForgetPasswordSerializer, UserSerializer


class CaptchaView(APIView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)
    serializer_class = CaptchaSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return simple_response(code=error_code.ERR_SERIALIZER_ERROR[0],
                                   message=serializer.errors)
        c_type = serializer.validated_data['c_type']
        app_id = serializer.validated_data.get('app_id', None)
        account = serializer.validated_data['account']
        code = None# 标志验证码是否发送成功
        message = None#标志额外消息
        # generate captcha
        captcha = captcha_generator()
        if account.isdigit():
            # send message
            code = 0
            message = 'ok'

        elif account.count('@') == 1:
            # send email
            pass
        else:
            return simple_response(code=error_code.ERR_SERIALIZER_ERROR,
                                   message="Account info error")
        if code == 0:
            Captcha.objects.create(
                account=account,
                app_id=app_id,
                captcha=captcha,
                c_type=c_type,
                expire_at=datetime.now() + timedelta(seconds=120)

            )
        return simple_response(code=code, message=message)


class SignupView(APIView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)
    serializer_class = SignupSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return simple_response(code=error_code.SUCCESS, message='create success')
        return simple_response(code=error_code.ERR_SERIALIZER_ERROR[0], message=serializer.errors)


class LoginView(APIView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return simple_response(code=error_code.ERR_SERIALIZER_ERROR[0],
                                   message=serializer.errors)
        try:
            user = User.objects.get(username=serializer.validated_data['username'])
        except User.DoesNotExist:
            try:
                user = User.objects.get(cellphone=serializer.validated_data['username'])
            except User.DoesNotExist:
                try:
                    user = User.objects.get(email=serializer.validated_data['username'])
                except User.DoesNotExist:
                    return simple_response(code=error_code.ERR_PARAM_ERROR[0],
                                           message='please enter right username or cellphone or email')

        if not user.check_password(serializer.validated_data['password']):
            return simple_response(code=error_code.ERR_PASSWORD_ERROR[0],
                                   message='password error')

        token = _general_token(user_id=user.id)
        return simple_response(code=error_code.SUCCESS,
                               message='ok', data=token)


class RefreshTokenView(APIView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RefreshTokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return simple_response(code=error_code.ERR_SERIALIZER_ERROR[0],
                                   message=serializer.errors)
        token = _refresh_token(serializer.validated_data['refresh_token'])
        return simple_response(code=error_code.SUCCESS,
                               message='refresh token ok', data=token)


class PasswordView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return simple_response(code=error_code.ERR_SERIALIZER_ERROR[0],
                                   message=serializer.errors)
        user = request.user
        if not user.check_password(serializer.validated_data['password']):
            return simple_response(*error_code.ERR_PASSWORD_ERROR)
        else:
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return simple_response(code=error_code.SUCCESS,
                                   message="successfully updated password")


class LogoutView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def delete(request):
        delete_token(request.user.id)
        logout(request)
        return simple_response(error_code.SUCCESS,
                               "successfully logout")


class ForgetPasswordView(APIView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)
    serializer_class = ForgetPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return simple_response(code=error_code.ERR_SERIALIZER_ERROR[0],
                                   message=serializer.errors)
        return simple_response(code=error_code.SUCCESS,
                               message="successfully reset password")


class UserView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    def get(self, request):
        serializer = self.serializer_class(request.user)
        return simple_response(code=error_code.SUCCESS,
                               message='ok', data = serializer.data)



def _refresh_token(refresh_token):
    user_id = get_refresh_token(refresh_token)
    if not user_id:
        raise ServerError(error_code=error_code.ERR_REFRESH_TOKEN_ERROR[0],
                          message=error_code.ERR_REFRESH_TOKEN_ERROR[1])
    refresh_token = _general_token(user_id, refresh_token)
    return refresh_token


def _general_token(user_id, refresh_token=None):
    """
    依据校验后的用户id生成token,或者用refresh token生成I
    :param user_id:
    :param refresh_token:
    :return: tokens
    """
    access_token = set_access_token(user_id)
    refresh_token = set_refresh_token(user_id, refresh_token)
    tokens = {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expired_in': ACCESS_TOKEN_EXPIRED_TIME
    }
    return tokens
