from django.conf.urls import url

from . import views

app_name = 'Ip_Mgmt'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='query_page'),
    url(r'^query', views.query_via_ip, name='query_via_ip'),
]
