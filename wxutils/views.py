from django.shortcuts import render
from django.contrib.auth.models import User, AnonymousUser
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_400_BAD_REQUEST,
                                   HTTP_401_UNAUTHORIZED)
from rest_framework.views import APIView
from utils.WXBizDataCrypt import WXBizDataCrypt
from cores.models import Staff
import requests
# Create your views here.

# class WxLoginView(APIView):
#     def post(self, request, *args, **kwargs):
#         app_id = 'wx2dd5acc1c7f3bc36'
#         secret = '0f7b8d33ffadfc7aba22f77f3569af45'
#         encrypted_data = request.POST.get('encrypted_data')
#         iv = request.POST.get('iv')
#         code =  request.POST.get('code')
#         code2SessionUrl = "https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={code}&grant_type=authorization_code".format(appid=app_id, secret=secret, code=code)
#         _res = requests.get(code2SessionUrl)
#         print(_res)
#         open_id = _res.json()["openid"]
#         session_key = _res.json()["session_key"]
#         pc = WXBizDataCrypt(app_id, session_key)
#         pc.decrypt(encrypted_data, iv)
#         phone_number = pc.decrypt(encrypted_data, iv)["purePhoneNumber"]
        
#         #根据手机号码判断是否存在此员工
#         try:
#             staff = Staff.objects.get(contact=phone_number)
#         except Staff.DoesNotExist as e:
#             return Response({
#                 'message': '不存在此员工',
#                 'code': '400001',
#                 'status': HTTP_200_OK,
#             })
#         except Staff.MultipleObjectsReturned as e:
#             return Response({
#                 'message': '存在多条记录',
#                 'code': '400002',
#                 'status': HTTP_200_OK,
#             })
#         if staff.wx_open_id == open_id:
#             pass
#         else:
#             staff.wx_open_id = open_id
#             staff.save()
#         try:
#             user = User.objects.get(username=phone_number,password=open_id)
#         except User.DoesNotExist as e:
#             return Response({
#                 'message': '手机号码与微信ID不匹配',
#                 'code': '400003',
#                 'status': HTTP_200_OK,
#             })
#         except User.MultipleObjectsReturned as e:
#             return Response({
#                 'message': '手机号码与微信ID不匹配',
#                 'code': '400003',
#                 'status': HTTP_200_OK,
#             })
#         return Response({
#             'message': 'success',
#             'data': {'open_id':open_id, 'phone_number':phone_number},
#             'status': HTTP_200_OK,
#         })