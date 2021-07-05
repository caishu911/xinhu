from django.template.loader import render_to_string
from django.http import HttpResponseNotFound, HttpResponseServerError, HttpResponseForbidden, HttpResponseBadRequest
from django.contrib.auth.models import User
from django.core.cache import cache
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_400_BAD_REQUEST,
                                   HTTP_401_UNAUTHORIZED)
from utils.WXBizDataCrypt import WXBizDataCrypt
import requests, json
from cores.models import Staff
from cores.serializers import StaffSerializer

def page_not_found(request, *args, **kwargs):
    return HttpResponseNotFound(render_to_string('404.html', request=request))

def forbidden(request, *args, **kwargs):
    return HttpResponseForbidden(render_to_string('403.html', request=request))

def server_error(request, *args, **kwargs):
    return HttpResponseServerError(render_to_string('500.html', request=request))

def bad_request(request, *args, **kwargs):
    return HttpResponseBadRequest(render_to_string('400.html', request=request))

def JwtResponsePayloadHandler(token, user=None, request=None):
    """
    自定义jwt认证成功返回数据
    """
    if user.is_superuser:
        
        return {
            'token': token,
            'user_id': user.id,
            'username': user.username
        }
    else:
        staff = Staff.objects.get(user=user)
        return {
            'token': token,
            'staff': StaffSerializer(staff).data,
        }

class CustomBackend(object):
    """jwt自定义用户验证"""
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username == 'wx':
            # print('password = ', password)
            cert_pair = json.loads(password)
            app_id = 'wx2dd5acc1c7f3bc36'
            secret = '0f7b8d33ffadfc7aba22f77f3569af45'
            print(cert_pair)
            encrypted_data = cert_pair['encrypted_data']
            iv = cert_pair['iv']
            code = cert_pair['code']
            code2SessionUrl = "https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={code}&grant_type=authorization_code".format(appid=app_id, secret=secret, code=code)
            _res = requests.get(code2SessionUrl)
            # print(_res)
            open_id = _res.json()["openid"]
            session_key = _res.json()["session_key"]
            pc = WXBizDataCrypt(app_id, session_key)
            pc.decrypt(encrypted_data, iv)
            phone_number = pc.decrypt(encrypted_data, iv)["purePhoneNumber"]

            #根据手机号码判断是否存在此员工
            try:
                staff = Staff.objects.get(contact=phone_number)
            except Staff.DoesNotExist as e:
                # 判断有组织营销中是否存在此员工
                return None
            except Staff.MultipleObjectsReturned as e:
                return None
            if staff.wx_open_id == open_id:
                pass
            else:
                staff.wx_open_id = open_id
                staff.save()
            if staff.user:
                if staff.user.check_password(staff.wx_open_id):
                    return staff.user
                else:
                    staff.user.set_password(staff.wx_open_id)
                    return staff.user
            else:
                try:
                    user = User.objects.get(username=phone_number)
                    staff.user = user
                    staff.save()
                    if user.check_password(open_id):
                        return user
                    else:
                        user.set_password(open_id)
                        return user
                except User.DoesNotExist as e:
                    user = User()
                    user.username = staff.contact
                    user.set_password(open_id)
                    user.save()
                    staff.user = user
                    staff.save()
                    return user
                except User.MultipleObjectsReturned as e:
                    return None
        else:
            pass

class UserRegisterView(GenericAPIView):
    
    def post(self, request, *args, **kwargs):
        if request.POST.get('name') and \
            request.POST.get('org_id') and \
            request.POST.get('iv') and \
            request.POST.get('code') and \
            request.POST.get('encrypted_data'):
            code = request.POST.get('code')
            iv = request.POST.get('iv')
            encrypted_data = request.POST.get('encrypted_data')
            app_id = 'wx2dd5acc1c7f3bc36'
            secret = '0f7b8d33ffadfc7aba22f77f3569af45'
            code2SessionUrl = "https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={code}&grant_type=authorization_code".format(appid=app_id, secret=secret, code=code)
            _res = requests.get(code2SessionUrl)
            open_id = _res.json()["openid"]
            session_key = _res.json()["session_key"]
            pc = WXBizDataCrypt(app_id, session_key)
            pc.decrypt(encrypted_data, iv)
            phone_number = pc.decrypt(encrypted_data, iv)["purePhoneNumber"]
            
            try:
                user = User.objects.get(username=phone_number)
                return Response({
                    'status': HTTP_200_OK,
                    'message': '注册失败，用户已存在',
                    'code': 40001
                })
            except User.DoesNotExist as e:
                user = User()
                user.username = phone_number
                user.is_active = False
                user.set_password(open_id)
                user.save()
                staff = Staff()
                staff.name = request.POST.get('name')
                staff.contact = phone_number
                staff.org_id = request.POST.get('org_id')
                staff.user = user
                staff.save()
                return Response({
                    'status': HTTP_200_OK,
                    'code': '20000',
                    'message': '注册成功，管理员授权后请在此号码的手机上登录'
                })
        else:
            return Response({
                'status': HTTP_200_OK,
                'code': '40000',
                'message': '注册失败，缺少参数'
            })