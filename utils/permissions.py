#coding=utf8
from rest_framework import permissions
from sqlmng.models import Inceptsql
from django.contrib.auth.models import Group
from utils.basemixins import AppellationMixins

SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')

class AuthOrReadOnly(AppellationMixins, permissions.BasePermission):

    def __init__(self):
        # 权限名
        self.allperms = ['execute', 'rollback', 'reject']
        # 权限规则
        self.auths = {
            self.dev: ['reject'],
            self.dev_mng: self.allperms,
            self.admin: self.allperms,
            self.dev_spm: self.allperms,
        }

    def has_permission(self, request, view):
        uri_list = request.META['PATH_INFO'].split('/')
        uri = uri_list[-2]
        if uri not in self.allperms:  # 非动作的操作（查询类的）
            return True
        pk = uri_list[-3]
        sqlobj = Inceptsql.objects.get(pk = pk)
        if sqlobj.env == self.env_test:  # 测试环境
            return True
        group_name = Group.objects.get(user=request.user).name
        return uri in self.auths[group_name] or request.user.is_superuser  # 用户的身份有操作权限 or 是超级用户
        # return sqlobj.treater == request.user.username or request.user.is_superuser  # SQL的执行人是用户 or 是超级用户

class IsSuperUser(permissions.BasePermission):
    """
    Allows access only to super users.
    """
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_superuser
