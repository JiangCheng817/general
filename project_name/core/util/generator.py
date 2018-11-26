# -*- coding:utf-8 -*-
#!/usr/bin/env python
# xiaoz
import random
import string


def captcha_generator(n=6):
    digits = string.digits
    captcha_list = random.sample(digits, n)
    return ''.join(captcha_list)



