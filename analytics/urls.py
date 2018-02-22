from django.conf.urls import url
from . import views
from .api.views import AccountRetrieveView

urlpatterns = [
    url(r'^$', views.info, name='info'),
    url(r'^api/(?P<server>\w+)/(?P<name>\w+)$', AccountRetrieveView.as_view(), name='api-info'),
]
