# -*- coding:utf-8 -*-
#!/usr/bin/env python
# xiaoz
from rest_framework.authentication import BaseAuthentication, get_authorization_header

from project_name.account.models import WebToken
from project_name.core.error_code import ERR_TOKEN_INVALID
from project_name.core.util.redis_relate import get_access_token, get_user_by_id
from project_name.utils.custom_exception import TokenAuthenticationFailed


class TokenAuthentication(BaseAuthentication):
    """
    Simple token based authentication.

    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Token ".  For example:

        Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
    """

    keyword = 'token'
    model = WebToken

    def get_model(self):
        if self.model is not None:
            return self.model
        from rest_framework.authtoken.models import Token
        return Token

    """
    A custom token model may be used, but must have the following properties.

    * key -- The string identifying the token
    * user -- The user to which the token belongs
    """

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != b'token':
            return None

        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise TokenAuthenticationFailed(code=ERR_TOKEN_INVALID[0],
                                            message=msg)
        elif len(auth) > 2:
            msg = 'Invalid token header. Token string should not contain spaces.'
            raise TokenAuthenticationFailed(code=ERR_TOKEN_INVALID[0],
                                            message=msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = 'Invalid token header. Token string should not contain invalid characters.'
            raise TokenAuthenticationFailed(code=ERR_TOKEN_INVALID[0],
                                            message=msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        # try:
        # token = self.model.objects.select_related('user').get(access_token=key)
        #             except self.model.DoesNotExist:
        #                 raise TokenAuthenticationFailed(code=ERROR_CODE_TOKEN_INVALID, message=_('Invalid token.'))
        #
        #             if token.at_is_expired():
        #                 raise TokenAuthenticationFailed(code=ERROR_CODE_TOKEN_IS_EXPIRED, message=_('Token is expired.'))
        #
        #             if not token.user.is_active:
        #                 raise TokenAuthenticationFailed(code=ERROR_CODE_TOKEN_INVALID,
        #                                                 message=_('User inactive or deleted.'))
        #
        #             return token.user, token
        user_id = get_access_token(key)
        if not user_id:
            msg = 'Invalid token.'
            raise TokenAuthenticationFailed(code=ERR_TOKEN_INVALID[0],
                                            message=msg)
        user = get_user_by_id(user_id)
        if not user.is_active:
            msg = 'User inactive or deleted.'
            raise TokenAuthenticationFailed(code=ERR_TOKEN_INVALID[0],
                                            message=msg)

        return user, None

    def authenticate_header(self, request):
        return 'token'