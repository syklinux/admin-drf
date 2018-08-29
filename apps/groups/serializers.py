
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from rest_framework import serializers

User = get_user_model()

# class Groupserializer(serializers.ModelSerializer):
#     """
#     group序列化类
#     """
#     def to_representation(self, instance):
#         member = instance.user_set.count()
#         ret = super(Groupserializer, self).to_representation(instance)
#         ret["member"] = member
#         return ret
#
#     class Meta:
#         model = Group
#         fields = ("id", "name")

class Groupserializer(serializers.ModelSerializer):
    """
    group序列化类,拿到组内成员个数并序列化输出
    """

    def to_permission_response(self, permission_queryset):
        ret = []
        # 将角色权限信息序列化
        for permission in permission_queryset:
            ret.append({
                'id': permission.id,
                'name': permission.name,
                'codename': permission.codename,
            })
        return ret

    def to_members_response(self, members_queryset):
        ret = []
        # 将角色用户信息序列化
        for member in members_queryset:
            ret.append({
                'id': member.id,
                'username': member.username,
                'name': member.name,
                'phone': member.phone
            })
        return ret

    def to_representation(self, instance):
        members = self.to_members_response(instance.user_set.all())
        number = instance.user_set.count()
        power = self.to_permission_response(instance.permissions.all())
        ret = super(Groupserializer, self).to_representation(instance)
        ret["members"] = members
        ret["number"] = number
        ret["power"] = power
        return ret

    class Meta:
        model = Group
        fields = ("id", "name")

class UserGroupsSerializer(serializers.ModelSerializer):
    """
    用户的角色 序列化类
    """
    groups = Groupserializer(many=True)

    def to_representation(self, instance):
        name = instance.name
        ret = super(UserGroupsSerializer, self).to_representation(instance)
        ret["name"] = name
        return ret

    class Meta:
        model = User
        fields = ("id", "username", "groups")