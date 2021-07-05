from re import L
from django.db import models
from rest_framework import fields, serializers
from poi.models import Poi, PoiDetail

class PoiDetailLiteSerializer(serializers.ModelSerializer):

    class Meta:
        model = PoiDetail
        fields = [
            'comment', 'image'
        ]

class PoiSerializer(serializers.ModelSerializer):

    create_date = serializers.DateTimeField(
        required=False, format="%Y-%m-%d", read_only=True)
    update_date = serializers.DateTimeField(
        required=False, format="%Y-%m-%d", read_only=True)
    # poi_detail = PoiDetailLiteSerializer(many=False, required=False, read_only=False)
    detail = serializers.SerializerMethodField(
        '_poi_detail', required=False, read_only=True
    )
    class Meta:
        model = Poi
        fields = [
            'id', 'lng_gcj_02', 'lat_gcj_02', 'lng_wgs_84', 'lat_wgs_84', 
            'lng_bd_09', 'lat_bd_09', 'name', 'creator_id', 'creator_name',
            'create_date', 'update_date', 'detail'
        ]
    
    def _poi_detail(self, obj):
        _poi = PoiDetail.objects.get(poi=obj)
        _serializer = PoiDetailLiteSerializer(_poi, many=False)
        return _serializer.data


class PoiDetailSerializer(serializers.ModelSerializer):
    create_date = serializers.DateTimeField(
        required=False, format="%Y-%m-%d", read_only=True)
    update_date = serializers.DateTimeField(
        required=False, format="%Y-%m-%d", read_only=True)
    poi = PoiSerializer(many=False, required=False, read_only=True)
    
    class Meta:
        model = PoiDetail
        fields = [
            'poi', 'comment', 'image', 'create_date', 'update_date'
        ]