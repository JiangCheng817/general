# -*- coding:utf-8 -*-
#!/usr/bin/env python
# xiaoz
from rest_framework import serializers


class ASerializers(serializers.Serializer):
    rate = serializers.CharField()