from django.conf.urls import url

from . import views

app_name = 'Core_Network_Arch'
urlpatterns = [
    # url(r'^$', views.IndexView.as_view(), name='index'),
    # url(r'^Report/Generating$', views.generate_report, name='generate_report'),
    url(r'^Report/$', views.ReportListView.as_view(), name='report_list'),
    url(r'^Report/([0-9]+)/$', views.ReportDetailView.as_view(), name='report_detail'),
    url(r'^Settings/$', views.SettingsMainView.as_view(), name='settings'),
    url(r'^Stats/(?P<pk>[0-9]+)/$', views.TrafficStatsDetailView.as_view(), name='trafficdetail'),
    # url(r'^TrafficDetail/RawData/(?P<pk>[0-9]+)/$', views.json_traffic_data_bulk, name='trafficdetail'),
    url(r'^TrafficDetail/BulkData$', views.json_traffic_data_bulk, name='trafficdetail'),
    url(r'^TrafficDetail/CreateTrafficStats$', views.create_single_traffic_data, name='create_stats'),
    url(r'^Report/CreateReport$', views.create_monthly_report, name='create_monthly_report')
]
