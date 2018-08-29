#coding=utf-8
from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter
from .views import *

# register的可选参数 base_name: 用来生成urls名字，如果viewset中没有包含queryset, base_name一定要有

# router = DefaultRouter()
# router.register(r'dbconfs', DbViewSet)
# router.register(r'inceptions', InceptionMainView, base_name='Inceptionmainview')
# router.register(r'inceptioncheck', InceptionCheckView, base_name='Inceptioncheckview')

urlpatterns = [
    # url(r'^', include(router.urls)),
    url(r'^autoselects/', SelectDataView.as_view(), name='selectdataview'),
]
