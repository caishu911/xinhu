from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_400_BAD_REQUEST,
                                   HTTP_401_UNAUTHORIZED)
# Create your views here.

class RegisterPromConfigView(GenericAPIView):
    def get(self, reqeust, *args, **kwargs):
        pass