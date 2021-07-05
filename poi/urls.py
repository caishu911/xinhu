from django.conf.urls import url
from poi.views import CreatePoiView, PoiView, PoiImageSharedLinkView, PoiByRangeView, TestView

urlpatterns = [
    url(r'^poi/create/$', CreatePoiView.as_view(), name='create_poi'),
    url(r'^poi/$', PoiView.as_view(), name='poi'),
    url(r'^poi/image/$', PoiImageSharedLinkView.as_view(), name='poi_image'),
    url(r'^poi/range/$', PoiByRangeView.as_view(), name='poi_by_range'),
    # url(r'^poi/test/1000/$', TestView, name='test'),
]