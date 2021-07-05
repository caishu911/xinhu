from django.db import models
import requests, json
from cores.models import Staff
from utils.oos_object import PoiObject
# Create your models here.
ak = "Bam0hNYPEOVIQfGx4ESwhXX3V6EImhpK"

# po = PoiObject()

class Poi(models.Model):
    '信息点模型'
    lng_gcj_02 = models.FloatField(null=False)
    lat_gcj_02 = models.FloatField(null=False)
    lng_wgs_84 = models.FloatField(null=True)
    lat_wgs_84 = models.FloatField(null=True)
    lng_bd_09 = models.FloatField(null=True)
    lat_bd_09 = models.FloatField(null=True)
    name = models.CharField(null=True, max_length=64)
    creator_id = models.IntegerField(null=False)
    create_date = models.DateTimeField(auto_now_add=True, auto_now=False)
    update_date = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        db_table = 'cm_poi'
    
    def convert_gcj_to_bd(self):
        r = requests.get('http://api.map.baidu.com/geoconv/v1/?coords={lng},{lat}&from={origin}&to={target}&ak={ak}'.format(
            lng=self.lng_gcj_02,
            lat=self.lat_gcj_02,
            origin=3,
            target=5,
            ak=ak
        ))
        self.lat_bd_09, self.lng_bd_09 = json.loads(r.text)["result"][0]["y"], json.loads(r.text)["result"][0]["x"]
        self.save()
    
    @classmethod
    def create(cls, name, lat_gcj_02, lng_gcj_02, creator_id):
        r = requests.get('http://api.map.baidu.com/geoconv/v1/?coords={lng},{lat}&from={origin}&to={target}&ak={ak}'.format(
            lng=lng_gcj_02,
            lat=lat_gcj_02,
            origin=3,
            target=5,
            ak=ak
        ))
        lat_bd_09, lng_bd_09 = json.loads(r.text)["result"][0]["y"], json.loads(r.text)["result"][0]["x"]
        poi = cls(name=name, lat_gcj_02=lat_gcj_02, lng_gcj_02=lng_gcj_02, creator_id=creator_id,lat_bd_09=lat_bd_09,lng_bd_09=lng_bd_09)
        return poi
    
    @property
    def creator_name(self):
        try:
            return Staff.objects.get(id=self.creator_id).name
        except Staff.DoesNotExist as e:
            return None
        except Staff.MultipleObjectsReturned as e:
            return None

    

class PoiDetail(models.Model):
    poi = models.OneToOneField(Poi, null=False, on_delete=models.CASCADE)
    comment = models.TextField(null=True)
    image = models.CharField(null=True, max_length=128)
    create_date = models.DateTimeField(auto_now_add=True, auto_now=False)
    update_date = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        db_table = 'ce_poi_detail'
    
    # @property
    # def image_share_link(self):
    #     return (po.generate_share_link(self.image))

def CreatePoi(lat, lng, name, creator_id,  comment=None):
        poi = Poi(
            name=name,
            lat_gcj_02=lat,
            lng_gcj_02=lng,
            creator_id=creator_id
        )
        poi.save()

