import os, json, datetime, sys, io, base64, re, requests
from django.contrib.auth.models import User
from typing_extensions import ParamSpecKwargs
from django.shortcuts import render
from django.views.generic import base
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_400_BAD_REQUEST,
                                   HTTP_401_UNAUTHORIZED)
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from pathlib import Path
from mysql import connector
from cores.models import MarketOrganization, Organization, Staff
# from utils.WXBizDataCrypt import WXBizDataCrypt
# Create your views here.

BASE_DIR = Path(__file__).resolve().parent.parent

# print(BASE_DIR)
# print(os.path.join(os.path.join(os.path.dirname(BASE_DIR), "marketapi")))

# /projects/www/marketapi

CONFIG_NAME = os.path.join(os.path.join(os.path.dirname(BASE_DIR), "marketapi"), 'config.json')
# print(CONFIG_NAME)
with open(CONFIG_NAME, "r") as f:
    DB_PARAMS = json.load(f)

class RoleView(GenericAPIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        if request.POST.get('name') and request.POST.get('category'):
            pass

class OrganizationView(GenericAPIView):
    def post(self, request, *args, **kwargs):
        if request.POST.get('name'):
            org = Organization()
            org.name = request.POST.get('name')
            if request.POST.get('parent_id'):
                try:
                    par_org = Organization.objects.get(id=request.POST.get('parent_id'))
                    org.parent_id = par_org.id
                    org.org_level = par_org.org_level + 1
                except Organization.DoesNotExist as e:
                    org.parent_id = -1
                    org.org_level = -1
                except Organization.MultipleObjectsReturned as e:
                    org.parent_id = -2
                    org.org_level = -2
            org.save()
            return Response({
                'status': HTTP_200_OK,
                'message': 'success'
            })
    
    def patch(self, request, *args, **kwargs):
        pass

class SearchStaffView(GenericAPIView):
    def get(self, request, *args, **kwargs):
        data = []
        if request.query_params.get('user_name') or \
            request.query_params.get('role_code') or \
            request.query_params.get('market_org_id'):
            cnx = connector.connect(
                host= str(base64.b64decode(DB_PARAMS['DB_HUZ_HC_3M']['HOST']),'utf-8'),
                port = str(base64.b64decode(DB_PARAMS['DB_HUZ_HC_3M']['PORT']),'utf-8'),
                user = str(base64.b64decode(DB_PARAMS['DB_HUZ_HC_3M']['USER']),'utf-8'),
                passwd = str(base64.b64decode(DB_PARAMS['DB_HUZ_HC_3M']['PASSWORD']),'utf-8'),
                db = str(base64.b64decode(DB_PARAMS['DB_HUZ_HC_3M']['NAME']),'utf-8'),
            )
            get_user_sql = """
                select
                    u.id,
                    replace(u.code, substr(u.code, 4, 6), repeat('*', 6)) user_name,
                    replace(u.name, substr(u.name, 2, 1), repeat('*', 1)) staff_name,
                    co.name org_name, 
                    group_concat(cr.code) role_code,
                    group_concat(cr.name) role_name
                from
                    core_user u,
                    core_org co,
                    core_user_role cur,
                    core_role cr,
                    core_org_market com 
                where
                    co.id = u.ORG_ID
                    and cur.user_id = u.id
                    and cr.id = cur.role_id
                    and com.id = u.market_org_id 
                    and u.del_flag = 0
                    {user_name_condition}
                    {user_role_condition}
                    {user_market_org_condition}
				group by u.id, user_name, staff_name, org_name
            """
            cur = cnx.cursor()
            if request.query_params.get('user_name') and re.match(r'^\d{11}$', request.query_params.get('user_name')):
                user_name_condition = "and u.code = '{user_name}'".format(user_name=request.query_params.get('user_name'))
            else:
                user_name_condition = " "
            if request.query_params.get('role_code'):
                user_role_condition = "and cr.code = '{role_code}'".format(role_code=request.query_params.get('role_code'))
            else:
                user_role_condition = " "
            if request.query_params.get('market_org_id'):
                user_market_org_condition = "and com.id = {market_org_id}".format(market_org_id=request.query_params.get('market_org_id'))
            else:
                user_market_org_condition = " "
            text = get_user_sql.format(
                user_name_condition=user_name_condition, 
                user_role_condition=user_role_condition, 
                user_market_org_condition=user_market_org_condition
            )
            cur.execute(text)
            keys = [x[0] for x in cur.description]            
            for value in cur.fetchall():
                data.append(dict(zip(keys, value)))
            cur.close()
            cnx.close()
            return Response({
                'status': HTTP_200_OK,
                'message': "success",
                'data': data
            })
        else:
            return Response({
                'status': HTTP_200_OK,
                'message': "fail",
                'data': data
            })

class SyncStaffView(GenericAPIView):
    
    def post(self, request, *args, **kwargs):
        data = []
        if request.POST.get('user_id'):
            cnx = connector.connect(
                host= str(base64.b64decode(DB_PARAMS['DB_HUZ_HC_3M']['HOST']),'utf-8'),
                port = str(base64.b64decode(DB_PARAMS['DB_HUZ_HC_3M']['PORT']),'utf-8'),
                user = str(base64.b64decode(DB_PARAMS['DB_HUZ_HC_3M']['USER']),'utf-8'),
                passwd = str(base64.b64decode(DB_PARAMS['DB_HUZ_HC_3M']['PASSWORD']),'utf-8'),
                db = str(base64.b64decode(DB_PARAMS['DB_HUZ_HC_3M']['NAME']),'utf-8'),
            )
            cur = cnx.cursor()
            for _id in request.POST.get('user_id').split(","):
                text = "select count(1) from core_user cu where cu.id = {id}".format(id=_id)
                cur.execute(text)
                cnt = list(cur)[0][0]
                if cnt == 1:
                    cur.execute("select cu.id, cu.name, cu.code, cu.org_id from core_user cu where cu.id = {id}".format(id=_id))
                    keys = [x[0] for x in cur.description]
                    values = cur.fetchall()[0]
                    _staff = dict(zip(keys, values))
                    try:
                        staff = Staff.objects.get(staff_3m_id=_staff["id"])
                        # staff.name = _staff["name"]
                        # staff.contact = _staff["code"]
                        # # staff.org_id = _staff["org_id"]
                        # staff.org_id = 102
                        # staff.save()
                    except Staff.DoesNotExist as e:
                        staff = Staff()
                        staff.staff_3m_id = _staff["id"]
                        staff.name = _staff["name"]
                        staff.contact = _staff["code"]
                        staff.org_id = _staff["org_id"]
                        staff.org_id = 102
                        staff.save()
                        user = User()
                        user.username = staff.contact
                        user.set_password(staff.wx_open_id)
                        user.save()
                    # return Response({
                    #     'status': HTTP_200_OK,
                    #     'message': "成功",
                    #     'staff': _staff
                    # })
                    pass
                else:
                    # return Response({
                    #     'status': HTTP_200_OK,
                    #     'message': "无此员工或存在多条记录"
                    # })
                    pass
            cur.close()
            cnx.close()
            return Response({
                'status': HTTP_200_OK,
                'message': "成功",
                'staff': _staff
            })
        else:
            return Response({
                'status': HTTP_200_OK,
                'message': "fail"
            })

class SyncOrganizationView(GenericAPIView):
    def get(self, request, *args, **kwargs):
        if request.query_params.get('org_id'):
            pass
        else:
            cnx = connector.connect(
                host= str(base64.b64decode(DB_PARAMS['DB_HUZ_HC_3M']['HOST']),'utf-8'),
                port = str(base64.b64decode(DB_PARAMS['DB_HUZ_HC_3M']['PORT']),'utf-8'),
                user = str(base64.b64decode(DB_PARAMS['DB_HUZ_HC_3M']['USER']),'utf-8'),
                passwd = str(base64.b64decode(DB_PARAMS['DB_HUZ_HC_3M']['PASSWORD']),'utf-8'),
                db = str(base64.b64decode(DB_PARAMS['DB_HUZ_HC_3M']['NAME']),'utf-8'),
            )
            cur = cnx.cursor()
            text = """
                select co1.id, 
                    co1.name, 
                    co2.NAME 
                from core_org co1, 
                    core_org co2 
                where co1.del_flag = 0 
                    and co1.code like '572%'
                    and co1.PARENT_ORG_ID = co2.id 
            """
            cur.execute(text)
            for value in cur.fetchall():
                try:
                    _org = Organization.objects.get(name=value[1])
                except Organization.DoesNotExist as e:
                    pass
                except Organization.MultipleObjectsReturned as e:
                    pass

            cur.close()
            cnx.close()
        return Response({
            'message': 'success',
            'status': HTTP_200_OK
        })

class SyncMarketOrganization(GenericAPIView):
    def get(self, request, *args, **kwargs):
        cnx = connector.connect(
            host= str(base64.b64decode(DB_PARAMS['DB_HUZ_HC_3M']['HOST']),'utf-8'),
            port = str(base64.b64decode(DB_PARAMS['DB_HUZ_HC_3M']['PORT']),'utf-8'),
            user = str(base64.b64decode(DB_PARAMS['DB_HUZ_HC_3M']['USER']),'utf-8'),
            passwd = str(base64.b64decode(DB_PARAMS['DB_HUZ_HC_3M']['PASSWORD']),'utf-8'),
            db = str(base64.b64decode(DB_PARAMS['DB_HUZ_HC_3M']['NAME']),'utf-8'),
        )
        cur = cnx.cursor()
        MarketOrganization.objects.all().delete()
        for _org in Organization.objects.filter(name='湖州分公司', org_3m_id__isnull=False):
            text = """
                select com.id,
                    com.name,
                    com.parent_org_id, 
                    com.parent_id 
                from core_org_market com 
                where del_flag = 0
                    and com.parent_org_id = {parent_org_id}
            """
            cur.execute(text.format(parent_org_id=_org.org_3m_id))
            for values in cur.fetchall():
                market_organization = MarketOrganization()
                market_organization.name = values[1]
                market_organization.org_id = values[2]
                market_organization.market_org_3m_id = values[0]
                market_organization.market_org_3m_parent_id = values[3]
                market_organization.c3_id = _org.c3_id
                market_organization.c4_id = _org.c4_id
                market_organization.save()
        
        return Response({
            'message': 'success',
            'status': HTTP_200_OK
        })

# class StaffView(GenericAPIView):
    
#     def post(self, request, *args, **kwargs):
#         if request.POST.get('staff_name') and request.POST.get()