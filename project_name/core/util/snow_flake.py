# -*- encoding: utf-8 -*-
import datetime
import os
import random
import threading
import time


DATACENTER_ID = int(os.getenv('DATACENTER_ID', 0))
assert 0 <= DATACENTER_ID <= 31

try:
    import uwsgi
except Exception:
    UWSGI = False
else:
    UWSGI = True


def _get_worker_id():
    return uwsgi.worker_id() - 1 if UWSGI else 0


# 2018-01-01T00:00:00Z
TWEPOCH = 1514764800000
TIMESTAMP_MS = 0
SEQUENCE_ID = 0
SHARD_NUM = 1 << 10


class SnowflakeId(object):
    """Initialize a new SnowflakeId.

    An SnowflakeId is a 64-bit unique identifier consisting of:

        - a 1-bit remaining 0,
        - a 41-bit value representing the miliseconds since the Unix epoch,
        - a 5-bit datacenter/server id,
        - a 5-bit worker/process id, and
        - a 12-bit counter, starting with a random value of 0~1023.

    By default, ``SnowflakeId()`` creates a new unique identifier. The
    optional parameter `sid` can be an :class:`SnowflakeId`, or any integer
    :class:`int` or, any base62 string :class:`str`.

    For example, the integer 15345254562157 do not follow the SnowflakeId
    specification but they are acceptable input::

        >>> SnowflakeId(15345254562157)
        SnowflakeId('4MA20J7F')

    `sid` can also be a :class:`str` which can be decoded via base62::

        >>> SnowflakeId('8a1bLYTvHe')
        SnowflakeId('8a1bLYTvHe')

    Raises :class:`ValueError` or :class:`TypeError` if `sid` is not acceptable.

    :Parameters:
        - `sid` (optional): a valid SnowflakeId.

    """
    _inc_lock = threading.Lock()

    __slots__ = ('__id')

    def __init__(self, sid=None):
        """Initialize a new SnowflakeId.

        """
        if sid is None:
            self.__generate()
        else:
            self.__validate(sid)

    @classmethod
    def from_datetime(cls, generation_time):
        """Create a dummy SnowflakeId instance with a specific generation time.

        This method is useful for doing range queries on a field
        containing :class:`SnowflakeId` instances.

        .. warning::
           It is not safe to insert a document containing an SnowflakeId
           generated using this method. This method deliberately
           eliminates the uniqueness guarantee that SnowflakeIds
           generally provide. SnowflakeIds generated with this method
           should be used exclusively in queries.

        `generation_time` will be converted to UTC. Naive datetime
        instances will be treated as though they already contain UTC.

        An example using this helper to get documents where ``"_id"``
        was generated before January 1, 2010 would be:

        >>> gen_time = datetime.datetime(2010, 1, 1)
        >>> dummy_id = SnowflakeId.from_datetime(gen_time)

        :Parameters:
          - `generation_time`: :class:`~datetime.datetime` to be used
            as the generation time for the resulting SnowflakeId.
        """
        if generation_time.utcoffset() is None:
            generation_time = generation_time.replace(tzinfo=datetime.timezone.utc)
        timestamp_ms = int(generation_time.timestamp() * 1000)
        sid = make_snowflake(timestamp_ms, 0, 0, 0, TWEPOCH)
        return cls(sid)

    @classmethod
    def from_timestamp(cls, timestamp):
        """Create a dummy SnowflakeId instance with a specific timestamp.
        """
        sid = make_snowflake(timestamp * 1000, 0, 0, 0, TWEPOCH)
        return cls(sid)

    @classmethod
    def from_timestamp_ms(cls, timestamp_ms):
        """Create a dummy SnowflakeId instance with a specific timestamp_ms.
        """
        sid = make_snowflake(timestamp_ms, 0, 0, 0, TWEPOCH)
        return cls(sid)

    @classmethod
    def from_now(cls):
        """Create a dummy SnowflakeId instance with a specific timestamp_ms.
        """
        timestamp_ms = int(time.time() * 1000)
        sid = make_snowflake(timestamp_ms, 0, 0, 0, TWEPOCH)
        return cls(sid)

    @classmethod
    def is_valid(cls, sid):
        """Checks if a `sid` string is valid or not.

        :Parameters:
          - `sid`: the object id to validate

        .. versionadded:: 2.3
        """
        if not sid:
            return False
        try:
            SnowflakeId(sid)
            return True
        except (TypeError, ValueError):
            return False

    def __generate(self):
        """Generate a new value for this SnowflakeId.
        """
        timestamp_ms = int(time.time() * 1000)

        with SnowflakeId._inc_lock:
            global TIMESTAMP_MS, SEQUENCE_ID
            if timestamp_ms == TIMESTAMP_MS:
                sequence_id = SEQUENCE_ID = SEQUENCE_ID + 1
            else:
                TIMESTAMP_MS = timestamp_ms
                sequence_id = SEQUENCE_ID = random.randint(0, SHARD_NUM - 1)
        worker_id = _get_worker_id()
        sid = make_snowflake(timestamp_ms, DATACENTER_ID, worker_id, sequence_id, TWEPOCH)
        self.__id = sid

    def __validate(self, sid):
        """Validate and use the given id for this SnowflakeId.

        Raises TypeError if id is not an instance of
        (:class:`basestring` (:class:`str` or :class:`bytes`
        in python 3), SnowflakeId) and InvalidId if it is not a
        valid SnowflakeId.

        :Parameters:
          - `sid`: a valid SnowflakeId
        """
        if isinstance(sid, int):
            if not -9223372036854775808 < sid < 9223372036854775807:
                raise ValueError("integer must be a valid 64-bit integer")
            self.__id = sid
        elif isinstance(sid, str):
            sid = base62.decode(sid)
            if not -9223372036854775808 < sid < 9223372036854775807:
                raise ValueError("base62 string must be abled to decoded to a valid 64-bit integer")
            self.__id = sid

        elif isinstance(sid, SnowflakeId):
            self.__id = sid.id
        else:
            raise TypeError("id must be an instance of (integer, base62 string, SnowflakeId)")

    @property
    def id(self):
        return self.__id

    @property
    def int(self):
        return self.__id

    @property
    def hex(self):
        return '%016x' % self.__id

    @property
    def b62(self):
        return base62.encode(self.__id)

    @property
    def timestamp_ms(self):
        return melt_timestamp_ms(self.__id, TWEPOCH)

    @property
    def datacenter_id(self):
        return melt_datacenter_id(self.__id)

    @property
    def worker_id(self):
        return melt_worker_id(self.__id)

    @property
    def sequence_id(self):
        return melt_sequence_id(self.__id)

    @property
    def shard_id(self):
        return self.sequence_id % SHARD_NUM

    @property
    def timestamp(self):
        return self.timestamp_ms // 1000

    @property
    def generation_time(self):
        """A :class:`datetime.datetime` instance representing the time of
        generation for this :class:`SnowflakeId`.

        The :class:`datetime.datetime` is timezone aware, and
        represents the generation time in UTC. It is precise to the
        second.
        """
        return datetime.datetime.fromtimestamp(self.timestamp_ms / 1000, datetime.timezone.utc)


    def __getstate__(self):
        """return value of object for pickling.
        needed explicitly because __slots__() defined.
        """
        return self.__id

    def __setstate__(self, value):
        """explicit state set from pickling
        """
        self.__id = value

    def __int__(self):
        return self.__id

    def __str__(self):
        return self.b62

    def __repr__(self):
        return "SnowflakeId('%s')" % str(self)

    def __eq__(self, other):
        if isinstance(other, SnowflakeId):
            return self.__id == other.id
        if isinstance(other, int):
            return self.__id == other
        if isinstance(other, str):
            return self.b62 == other
        if isinstance(other, datetime.datetime):
            return self.generation_time == other
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, SnowflakeId):
            return self.__id != other.id
        if isinstance(other, int):
            return self.__id != other
        if isinstance(other, str):
            return self.b62 != other
        if isinstance(other, datetime.datetime):
            return self.generation_time != other
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, SnowflakeId):
            return self.__id < other.id
        if isinstance(other, int):
            return self.__id < other
        if isinstance(other, str):
            return self.b62 < other
        if isinstance(other, datetime.datetime):
            return self.generation_time < other
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, SnowflakeId):
            return self.__id <= other.id
        if isinstance(other, int):
            return self.__id <= other
        if isinstance(other, str):
            return self.b62 <= other
        if isinstance(other, datetime.datetime):
            return self.generation_time <= other
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, SnowflakeId):
            return self.__id > other.id
        if isinstance(other, int):
            return self.__id > other
        if isinstance(other, str):
            return self.b62 > other
        if isinstance(other, datetime.datetime):
            return self.generation_time > other
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, SnowflakeId):
            return self.__id >= other.id
        if isinstance(other, int):
            return self.__id >= other
        if isinstance(other, str):
            return self.b62 >= other
        if isinstance(other, datetime.datetime):
            return self.generation_time >= other
        return NotImplemented

    def __hash__(self):
        """Get a hash value for this :class:`SnowflakeId`."""
        return hash(self.__id)


# twitter's snowflake parameters
# twepoch = 0
datacenter_id_bits = 5
worker_id_bits = 5
sequence_id_bits = 12
max_datacenter_id = 1 << datacenter_id_bits
max_worker_id = 1 << worker_id_bits
max_sequence_id = 1 << sequence_id_bits
max_timestamp = 1 << (64 - datacenter_id_bits - worker_id_bits - sequence_id_bits)


def make_snowflake(timestamp_ms, datacenter_id, worker_id, sequence_id, twepoch=0):
    """generate a twitter-snowflake id, based on
    https://github.com/twitter/snowflake/blob/master/src/main/scala/com/twitter/service/snowflake/IdWorker.scala
    :param: timestamp_ms time since UNIX epoch in milliseconds"""
    sid = ((int(timestamp_ms) - twepoch) % max_timestamp) << datacenter_id_bits << worker_id_bits << sequence_id_bits
    sid += (datacenter_id % max_datacenter_id) << worker_id_bits << sequence_id_bits
    sid += (worker_id % max_worker_id) << sequence_id_bits
    sid += sequence_id % max_sequence_id
    return sid


def melt(snowflake_id, twepoch=0):
    """inversely transform a snowflake id back to its parts."""
    sequence_id = snowflake_id & (max_sequence_id - 1)
    worker_id = (snowflake_id >> sequence_id_bits) & (max_worker_id - 1)
    datacenter_id = (snowflake_id >> sequence_id_bits >> worker_id_bits) & (max_datacenter_id - 1)
    timestamp_ms = snowflake_id >> sequence_id_bits >> worker_id_bits >> datacenter_id_bits
    timestamp_ms += twepoch
    return (timestamp_ms, datacenter_id, worker_id, sequence_id)


def melt_timestamp_ms(snowflake_id, twepoch=0):
    """inversely transform a snowflake id back to its parts."""
    timestamp_ms = snowflake_id >> sequence_id_bits >> worker_id_bits >> datacenter_id_bits
    timestamp_ms += twepoch
    return timestamp_ms


def melt_datacenter_id(snowflake_id, twepoch=0):
    """inversely transform a snowflake id back to its parts."""
    datacenter_id = (snowflake_id >> sequence_id_bits >> worker_id_bits) & (max_datacenter_id - 1)
    return datacenter_id


def melt_worker_id(snowflake_id, twepoch=0):
    """inversely transform a snowflake id back to its parts."""
    worker_id = (snowflake_id >> sequence_id_bits) & (max_worker_id - 1)
    return worker_id


def melt_sequence_id(snowflake_id, twepoch=0):
    """inversely transform a snowflake id back to its parts."""
    sequence_id = snowflake_id & (max_sequence_id - 1)
    return sequence_id


# Copyright (c) 2010 Guilherme Gondim. All rights reserved.
# Copyright (c) 2009 Simon Willison. All rights reserved.
# Copyright (c) 2002 Drew Perttula. All rights reserved.
#
# License:
#   Python Software Foundation License version 2
#
# See the file "LICENSE" for terms & conditions for usage, and a DISCLAIMER OF
# ALL WARRANTIES.
#
# This Baseconv distribution contains no GNU General Public Licensed (GPLed)
# code so it may be used in proprietary projects just like prior ``baseconv``
# distributions.
#
# All trademarks referenced herein are property of their respective holders.
#

"""
Convert numbers from base 10 integers to base X strings and back again.

Sample usage::

  >>> base20 = BaseConverter('0123456789abcdefghij')
  >>> base20.encode(1234)
  '31e'
  >>> base20.decode('31e')
  1234
  >>> base20.encode(-1234)
  '-31e'
  >>> base20.decode('-31e')
  -1234
  >>> base11 = BaseConverter('0123456789-', sign='$')
  >>> base11.encode('$1234')
  '$-22'
  >>> base11.decode('$-22')
  '$1234'

"""

BASE2_ALPHABET = '01'
BASE16_ALPHABET = '0123456789ABCDEF'
BASE56_ALPHABET = '23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz'
BASE36_ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyz'
BASE62_ALPHABET = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
BASE64_ALPHABET = BASE62_ALPHABET + '-_'


class BaseConverter:
    decimal_digits = '0123456789'

    def __init__(self, digits, sign='-'):
        self.sign = sign
        self.digits = digits
        if sign in self.digits:
            raise ValueError('Sign character found in converter base digits.')

    def __repr__(self):
        return "<%s: base%s (%s)>" % (self.__class__.__name__, len(self.digits), self.digits)

    def encode(self, i):
        neg, value = self.convert(i, self.decimal_digits, self.digits, '-')
        if neg:
            return self.sign + value
        return value

    def decode(self, s):
        neg, value = self.convert(s, self.digits, self.decimal_digits, self.sign)
        if neg:
            value = '-' + value
        return int(value)

    def convert(self, number, from_digits, to_digits, sign):
        if str(number)[0] == sign:
            number = str(number)[1:]
            neg = 1
        else:
            neg = 0

        # make an integer out of the number
        x = 0
        for digit in str(number):
            x = x * len(from_digits) + from_digits.index(digit)

        # create the result in base 'len(to_digits)'
        if x == 0:
            res = to_digits[0]
        else:
            res = ''
            while x > 0:
                digit = x % len(to_digits)
                res = to_digits[digit] + res
                x = int(x // len(to_digits))
        return neg, res


base2 = BaseConverter(BASE2_ALPHABET)
base16 = BaseConverter(BASE16_ALPHABET)
base36 = BaseConverter(BASE36_ALPHABET)
base56 = BaseConverter(BASE56_ALPHABET)
base62 = BaseConverter(BASE62_ALPHABET)
base64 = BaseConverter(BASE64_ALPHABET, sign='$')
