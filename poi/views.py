from django.db.models.query_utils import Q
from django.shortcuts import render
from rest_framework.generics import GenericAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_400_BAD_REQUEST,
                                   HTTP_401_UNAUTHORIZED)
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from ooscore.client import Config
import ooscore.exceptions as exceptions
import traceback
from poi.models import Poi, PoiDetail
from poi.serializers import PoiSerializer, PoiDetailSerializer
from utils.oos_object import PoiObject
import time, math, requests
from cores.models import Staff
import json, oos
# Create your views here.

poi_object = PoiObject()

# # 6.0 Server
# __ACCESS_KEY = '354afcdf7693df85dc5f'                                     # your id
# __SECRET_KEY = '7167f024d4791dac4a0713dbe9687b6b58b5ea16'                 # your key
# __ENDPOINT = 'http://oos-cn.ctyunapi.cn'                                  #
# __IAM_ENDPOINT = 'http://oos-cn-iam.ctyunapi.cn'                          # your domain
# __SIGNATURE_VERSION = 's3v4'                                              # signer version V4 's3v4'
# # SIGNATURE_VERSION = 's3'                                              # signer version V2 's3'
# __SERVICE_NAME = 's3'
# __IAM_SERVICE_NAME = 'sts'

# __BUCKET = 'hudx-poi-oos'
# KEY = ''
# # MULTIPART_UPLOAD_KEY = 'test-multi'
# UPLOAD_FILE = ''
# # DOWNLOAD_FILE_PATH = './foo'
# __API_VERSION = '2006-03-01'
# if __ENDPOINT.lower().find("http") < 0 and __ENDPOINT.lower().find("https") < 0:
#     __ENDPOINT = "http://" + __ENDPOINT

# if __IAM_ENDPOINT.lower().find("http") < 0 and __IAM_ENDPOINT.lower().find("https") < 0:
#     __IAM_ENDPOINT = "http://" + __IAM_ENDPOINT
# try:
#     _config = Config(endpoint_url=__ENDPOINT, signature_version=__SIGNATURE_VERSION,
#                     s3={'payload_signing_enabled': True})

#     _iam_config = Config(endpoint_url=__IAM_ENDPOINT, signature_version=__SIGNATURE_VERSION,
#                         s3={'payload_signing_enabled': True})

#     client = oos.client(service_name=__SERVICE_NAME, use_ssl=False, endpoint_url=__ENDPOINT, api_version=__API_VERSION,
#                         access_key_id=__ACCESS_KEY, secret_access_key=__SECRET_KEY,
#                         config=_config)

#     iam_client = oos.client(service_name=__IAM_SERVICE_NAME, use_ssl=False, endpoint_url=__IAM_ENDPOINT,
#                             access_key_id=__ACCESS_KEY, secret_access_key=__SECRET_KEY,
#                             config=_iam_config)
# except Exception as ex:
#     print(traceback.format_exc())
#     print(ex)
#     exit(-1)

# def handle_error(fn):
#     def inner(self):
#         try:
#             fn(self)
#         except exceptions.ClientError as e:
#             print('\n Response code: {0}\n Error message: {1}\n Resource: {2}\n request id: {3}'
#                 .format(e.response['Error']['Code'],
#                         e.response['Error']['Message'],
#                         e.response['Error']['Resource'],
#                         e.response['ResponseMetadata']['RequestId']
#                         ))
#     return inner
def coordinate_convert(lat, lng, c_type):
    ak = "Bam0hNYPEOVIQfGx4ESwhXX3V6EImhpK"
    if c_type == 'gcj-02':
        r = requests.get('http://api.map.baidu.com/geoconv/v1/?coords={lng},{lat}&from={origin}&to={target}&ak={ak}'.format(
            lng=lng,
            lat=lat,
            origin=3,
            target=5,
            ak=ak
        ))
        return (json.loads(r.text)["result"][0]["y"], json.loads(r.text)["result"][0]["x"])
    elif c_type == 'wgs-84':
        pass
    elif c_type == 'bd-09':
        pass
    else:
        pass

class CreatePoiView(GenericAPIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        if request.POST.get('name') and \
            request.POST.get('lat') and \
            request.POST.get('lng') and \
            request.FILES.getlist('files'):
            print(request.POST.get('name'), request.POST.get('lat'), request.POST.get('lng'))
            poi = Poi.create(
                name=request.POST.get('name'),
                lat_gcj_02=request.POST.get('lat'),
                lng_gcj_02=request.POST.get('lng'),
                creator_id=Staff.objects.get(user=request.user).id
            )
            # poi.lat_gcj_02 = request.POST.get('lat')
            # poi.lng_gcj_02 = request.POST.get('lng')
            # poi.lat_bd_09, poi.lng_bd_09 = coordinate_convert(poi.lat_gcj_02, poi.lng_gcj_02, 'gcj-02')
            # poi.name = request.POST.get('name')
            # poi.creator_id = Staff.objects.get(user=request.user).id
            poi.save()
            image_key = str(round(time.time() * 1000)) + '.' + str(request.FILES.getlist('files')[0]).split('.')[1]
            try:
                poi_detail = PoiDetail.objects.get(poi=poi)
                poi_detail.comment = request.POST.get('comment') or poi_detail.comment
                poi_detail.image = image_key
                poi_detail.save()
            except PoiDetail.DoesNotExist as e:
                poi_detail = PoiDetail()
                poi_detail.poi = poi
                poi_detail.comment = request.POST.get('comment')
                poi_detail.image = image_key
                poi_detail.save()
            except PoiDetail.MultipleObjectsReturned as e:
                pass
            poi_object.key = request.FILES.getlist('files')[0]
            poi_object.UPLOAD_FILE = request.FILES.getlist('files')[0]
            poi_object.KEY = image_key
            poi_object.put_image()
            return Response({
                'message': '提交成功',
                'status': HTTP_200_OK
            })
        else:
            return Response({
                'code': 40001,
                'message': '提交数据不完整',
                'status': HTTP_200_OK
            })

class PoiView(GenericAPIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        if request.query_params.get('name') or request.query_params.get('id'):
            condition = Q()
            condition.connector = 'AND'
            if request.query_params.get('name') or request.query_params.get('name') != '':
                condition.add(
                    Q(name__icontains=request.query_params.get('name')), 'AND'
                )
            if request.query_params.get('id'):
                condition.add(
                    Q(id=request.query_params.get('id')), 'AND'
                )
            poi = Poi.objects.filter(condition)
            paginator = PageNumberPagination()
            paginator.page_size = 10
            result_page = paginator.paginate_queryset(poi, request)
            serializer = PoiSerializer(result_page, many=True)
            return paginator.get_paginated_response({
                'code': '20000',
                'message': 'success',
                'data': serializer.data,
                'status': HTTP_200_OK
            })
        elif request.query_params.get('ne') and request.query_params.get('sw'):
            [ne_lng, ne_lat] = request.query_params.get('ne').split(",")
            [sw_lng, sw_lat] = request.query_params.get('sw').split(",")
            poi = Poi.objects.filter(lng_gcj_02__lte=ne_lng,lng_gcj_02__gte=sw_lng,lat_gcj_02__lte=ne_lat, lat_gcj_02__gte=sw_lat)
            paginator = PageNumberPagination()
            paginator.page_size = 10
            result_page = paginator.paginate_queryset(poi, request)
            serializer = PoiSerializer(result_page, many=True)
            return paginator.get_paginated_response({
                'code': '20000',
                'message': 'success',
                'data': serializer.data,
                'status': HTTP_200_OK
            })
        else:
            # staff = Staff.objects.get(user=request.user)
            # poi = Poi.objects.filter(creator_id=staff.id)
            # paginator = PageNumberPagination()
            # paginator.page_size = 10
            # result_page = paginator.paginate_queryset(poi, request)
            # serializer = PoiSerializer(result_page, many=True)
            # return paginator.get_paginated_response({
            #     'message': 'success',
            #     'data': serializer.data,
            #     'status': HTTP_200_OK
            # })
            return Response({
                'code': 40001,
                'message': '',
                'data': None,
                'status': HTTP_200_OK
            })

class PoiByRangeView(GenericAPIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        if request.query_params.get('ne') and request.query_params.get('sw'):
            [ne_lng, ne_lat] = request.query_params.get('ne').split(",")
            [sw_lng, sw_lat] = request.query_params.get('sw').split(",")
            poi = Poi.objects.filter(lng_gcj_02__lte=ne_lng,lng_gcj_02__gte=sw_lng,lat_gcj_02__lte=ne_lat, lat_gcj_02__gte=sw_lat)
            # paginator = PageNumberPagination()
            # paginator.page_size = 10
            # result_page = paginator.paginate_queryset(poi, request)
            # return paginator.get_paginated_response({
            #     'message': 'success',
            #     'data': serializer.data,
            #     'status': HTTP_200_OK
            # })
            serializer = PoiSerializer(poi, many=True)
            return Response({
                'message': 'success',
                'data': serializer.data,
                'status': HTTP_200_OK
            })

        else:
            return Response({
                'code': 40001,
                'message': '坐标错误',
                'status': HTTP_200_OK
            })

class PoiImageSharedLinkView(GenericAPIView):
    def get(self, request,*args, **kwargs):
        if request.query_params.get('poi_id'):
            try:
                p = Poi.objects.get(id=request.query_params.get('poi_id'))
                pd = PoiDetail.objects.get(poi=p)
                poi_object = PoiObject()
                poi_object.KEY = pd.image
                shared_link = poi_object.generate_shared_link()
                return Response({
                    'status': HTTP_200_OK,
                    'message': 'success',
                    'url': shared_link
                })
            except Poi.DoesNotExist as e:
                return None
            except Poi.MultipleObjectsReturned as e:
                return None
            except PoiDetail.DoesNotExist as e:
                return None
            except PoiDetail.MultipleObjectsReturned as e:
                return None

        else:
            return Response({
                'status': HTTP_200_OK,
                'message': 'missing params',
                'data': None
            })