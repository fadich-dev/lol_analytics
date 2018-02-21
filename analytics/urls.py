from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.info, name='info'),
    url(r'^api/(?P<region>\w+)/(?P<account>\w+)/$', views.api_info, name='api-info'),
]
