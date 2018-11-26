# -*- coding:utf-8 -*-
#!/usr/bin/env python
# xiaoz
import random
import string
import uuid


def captcha_generator(n=6):
    digits = string.digits
    captcha_list = random.sample(digits, n)
    return ''.join(captcha_list)


# 生成终端ID
def gen_enduser_id():
    return str(uuid.uuid1()).replace("-", "")


# 生成产品ID
def gen_product_id():
    return str(uuid.uuid1()).replace("-", "")


# 生成APP ID
def gen_app_id():
    return str(uuid.uuid1()).replace("-", "")

