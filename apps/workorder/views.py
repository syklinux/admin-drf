# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from rest_framework import viewsets, mixins,permissions, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authentication import TokenAuthentication,BasicAuthentication,SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication


from .serializers import WorkOrderSerializer
from .models import WorkOrder

User = get_user_model()


class Pagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = "page"
    max_page_size = 100


class WorkOrderViewset(viewsets.ModelViewSet):
    """
    create:
    创建工单
    list:
    获取工单列表
    retrieve:
    获取工单信息
    update:
    更新更新信息
    delete:
    删除用户
    """
    authentication_classes = (JSONWebTokenAuthentication, TokenAuthentication, SessionAuthentication, BasicAuthentication)
    permission_classes = (permissions.IsAuthenticated,permissions.DjangoObjectPermissions)
    queryset = WorkOrder.objects.all()
    serializer_class = WorkOrderSerializer
    pagination_class = Pagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('title',)
    ordering_fields = ('id',)

    def get_queryset(self):
        status = self.request.GET.get('status', None)
        applicant = self.request.user
        role = applicant.groups.all().values('name')
        role_name = [r['name'] for r in role]
        queryset = super(WorkOrderViewset, self).get_queryset()
        # 判断传来的status值判断是申请列表还是历史列表
        if status and int(status) == 1:
            queryset = queryset.filter(status__lte=int(status))
        elif status and int(status) == 2:
            queryset = queryset.filter(status__gte=int(status))
        else:
            pass

        # 判断登陆用户是否是管理员，是则显示所有工单，否则只显示自己的
        if "ops" not in role_name:
            queryset = queryset.filter(applicant=applicant)
        return queryset

    def partial_update(self,requests, *args,**kwargs):
        pk = int(kwargs.get("pk"))
        final_processor = self.request.user
        data = requests.data
        data['final_processor'] = final_processor
        isinstance = WorkOrder.objects.filter(pk=pk).update(**data)
        return Response(status=status.HTTP_204_NO_CONTENT)
