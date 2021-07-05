from django.conf.urls import url
from cores.views import SearchStaffView, SyncStaffView, OrganizationView, SyncOrganizationView, SyncMarketOrganization


urlpatterns = [
    url(r'^search_staff/$', SearchStaffView.as_view(), name='search_staff'),
    url(r'^sync_staff/$', SyncStaffView.as_view(), name='sync_staff'),
    url(r'^org/$', OrganizationView.as_view(), name='organization'),
    url(r'^org/sync/$', SyncOrganizationView.as_view(), name='sync_org'),
    url(r'^market_org/sync/$', SyncMarketOrganization.as_view(), name='sync_market_org'),
]