# -*- coding:utf-8 -*-
#!/usr/bin/env python
# xiaoz
import os
from hashlib import sha1

from django.core.cache import caches, cache

from project_name.account.models import User
from project_name.core import error_code
from project_name.core.util.snow_flake import SnowflakeId
from project_name.utils.custom_exception import ServerError

ACCESS_TOKEN_EXPIRED_TIME = 60*60
REFRESH_TOKEN_EXPIRED_TIME = 60*60*6


def set_access_token(user_id):
    sid = SnowflakeId(user_id)
    access_token = sid.b62 + ':' + sha1(os.urandom(24)).hexdigest()
    key = 'token:access:%s' % access_token
    caches['json'].set(key, user_id, timeout=ACCESS_TOKEN_EXPIRED_TIME)
    return access_token


def set_refresh_token(user_id, refresh_token=None):
    if refresh_token is None:
        sid = SnowflakeId(user_id)
        refresh_token = sid.b62 + ":" + sha1(os.urandom(24)).hexdigest()
    key = 'token:refresh:%s' % refresh_token
    caches['json'].set(key, user_id, timeout=REFRESH_TOKEN_EXPIRED_TIME)
    return refresh_token


def get_refresh_token(refresh_token):
    key = 'token:refresh:%s' % refresh_token
    value = caches['json'].get(key)
    return value


def get_access_token(access_token):
    key = 'token:access:%s' % access_token
    value = caches['json'].get(key)
    return value


def set_user_cache(user):
    key = 'user:id:%s' % user.id
    cache.set(key, user, REFRESH_TOKEN_EXPIRED_TIME)


def get_user_cache(user_id):
    key = 'user:id:%s' % user_id
    value = cache.get(key)
    return value


def get_user_by_id(user_id):
    """
    从缓存取user对象，不存在则从数据库取，存入缓存
    """
    user = get_user_cache(user_id=user_id)
    if user is None:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ServerError(*error_code.ERR_USER_NOT_EXIST)
        set_user_cache(user)
    return user


def delete_token(user_id):
    sid = SnowflakeId(user_id)
    caches['json'].delete_pattern("token:refresh:%s*" % sid)
    caches['json'].delete_pattern("token:access:%s*" % sid)

