from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework import permissions

from .serializers import CaptchaSerializer


class CaptchaView(APIView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)
    serializer_class = CaptchaSerializer

    def post(self):
        serializer = self.serializer_class
