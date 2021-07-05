from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer

from cores.models import Organization, Staff

class OrganizationSerializer(ModelSerializer):
    create_date = serializers.DateTimeField(
        required=False, format="%Y-%m-%d", read_only=True)
    update_date = serializers.DateTimeField(
        required=False, format="%Y-%m-%d", read_only=True)
    
    class Meta:
        model = Organization
        fields = [
            'name','c3_id', 'c3_name', 'c4_id', 'c4_name', 'org_tree', 'org_level', 'parent_id', 'org_3m_id',
            'create_date', 'update_date'
        ]

class StaffSerializer(ModelSerializer):
    'STAFF序列化'
    create_date = serializers.DateTimeField(
        required=False, format="%Y-%m-%d", read_only=True)
    update_date = serializers.DateTimeField(
        required=False, format="%Y-%m-%d", read_only=True)
    organization = OrganizationSerializer(required=False, read_only=True)
    class Meta:
        model = Staff
        fields = [
            'id', 'name', 'id_number', 'contact', 'org_id', 'staff_3m_id',
            'organization', 'create_date', 'update_date'
        ]
