# -*- coding:utf-8 -*-
#!/usr/bin/env python
# xiaoz
from rest_framework import status
from rest_framework.response import Response


# 封装了response,增加 code 和 message 字段。并以data={'meta':{'code':code,'message':messgae},'data':data}的
# 的形式返回
def simple_response(code, message, data={}, status=status.HTTP_200_OK, headers=None):
    """
    精简Response
    Args:
        code: 错误code
        message: 提示信息
        data: 返回数据
        status: http状态code
        headers: http headers
    Returns: Response

    """
    meta = {'code': code, 'message': message}
    return Response(data={'meta': meta, 'data': data}, status=status, headers=headers)