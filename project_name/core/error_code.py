# -*- coding:utf-8 -*-
#!/usr/bin/env python
# xiaoz

SUCCESS = 0

# param: 10000~ 10049
ERR_PARAM_ERROR = (10000, "params error")
ERR_SERIALIZER_ERROR = (10002, "serializer error")

# token: 10100 ~ 10149
ERR_TOKEN_IS_EXPIRED = (10100, "token is expired")
ERR_TOKEN_INVALID = (10101, "token is invalid")
ERR_REFRESH_TOKEN_ERROR = (10102, "refresh token is expired or invalid")  # expired or invalid

# User: 10150 ~ 10199
ERR_USER_NOT_EXIST = (10150, "user is not existence")
ERR_USER_INACTIVE = (10151, "user is inactive")

# password: 10200~10249
ERR_PASSWORD_ERROR = (10200, 'password error')

# faq: 10250~10499
ERR_SUPPORT_NOT_EXIST = (10250, 'support does not exist')