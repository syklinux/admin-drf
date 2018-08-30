from rest_framework import  viewsets
from .models import Cabinet
from .serializers import CabinetSerializer
from .filter import CabinetFilter
from rest_framework import permissions

class CabinetViewset(viewsets.ModelViewSet):
    """
    list:
    返回机柜列表

    create:
    创建机柜记录

    retrieve:
    返回机柜记录

    destroy
    删除机柜记录

    update:
    更新机柜记录
    """
    permission_classes = (permissions.IsAuthenticated, permissions.DjangoObjectPermissions)
    queryset = Cabinet.objects.all()
    serializer_class = CabinetSerializer
    filter_class = CabinetFilter
    filter_fields = ("name", "idc")

