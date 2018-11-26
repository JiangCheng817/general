from django.shortcuts import render

# Create your views here.
from rest_framework import permissions
from rest_framework.views import APIView

from project_name.core import error_code
from .serializer import SignupSerializer
from project_name.utils.custom_response import simple_response


class SignupView(APIView):
    class SignupView(APIView):
        authentication_classes = ()
        permission_classes = (permissions.AllowAny,)
        serializer_class = SignupSerializer

        def post(self, request):
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return simple_response(code=error_code.SUCCESS, message='create success')
            return simple_response(code=error_code.ERR_SERIALIZER_ERROR[0], message=serializer.errors)
