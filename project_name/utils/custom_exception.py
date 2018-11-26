# -*- coding:utf-8 -*-
#!/usr/bin/env python
# xiaoz

from __future__ import unicode_literals
from django.utils.encoding import force_text, six

from rest_framework import status
from rest_framework.exceptions import APIException


# 重新封装了APIException ,让返回的数据格式为{'data':data,"meta":{
# 'code':code,'messsage':'message'}}
class ServerError(APIException):

    status_code = status.HTTP_200_OK
    default_message = 'A server error occurred.'

    def __init__(self, error_code=None, message=None):
        if not error_code:
            self.error_code = self.status_code
        else:
            self.error_code = error_code

        if message:
            self.message = force_text(message)
            self.detail = {
                "data": {},
                "meta":
                    {
                    "code": self.error_code,
                    "message": self.message
                }
        }
        else:
            self.message = six.text_type(self.default_message)
            self.detail = {
                "data": {},
                "meta":
                    {
                        "code": self.error_code,
                        "message": self.message
                    }
        }

    def __str__(self):
        return six.text_type(self.message)

    def get_codes(self):
        """
        Return only the code part of the error details.

        Eg. {"name": ["required"]}
        """
        return self.error_code

    def get_full_details(self):
        payload = {
            "code": self.error_code,
            "message": self.message
        }
        return payload


class TokenAuthenticationFailed(APIException):
    status_code = status.HTTP_200_OK
    default_detail = 'Incorrect authentication credentials.'

    def __init__(self, code=0, message=None):
        if message is not None:
            meta = {'code': code, 'message': message}
        else:
            meta = {'code': code, 'message': self.default_detail}
        data = {}
        self.detail = {'meta': meta, 'data': data}

    def __str__(self):
        return six.text_type(self.detail)