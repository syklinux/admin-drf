# -*- coding:utf-8 -*-
from rest_framework import serializers
from .models import *
from utils.dbcrypt import prpcrypt
from users.models import User

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username')

class InceptionSerializer(serializers.ModelSerializer):

    users = serializers.CharField(required=False)
    class Meta:
        model = Inceptsql
        fields = '__all__'

    def to_representation(self, instance):
        ret = super(InceptionSerializer, self).to_representation(instance)
        users = [{'id':u.id, 'name':u.username} for u in instance.users.all()]
        ret["users"] = users
        ret['db_name'] = instance.db.name
        return ret

    def create(self, validated_data):
        print(validated_data)
        validated_data['db'] = Dbconf.objects.get(id = validated_data['db'])
        treater = User.objects.get_or_create(username = validated_data.get('treater'))[0]  # 经理数据
        commiter = validated_data.get('commiter')
        validated_data['treater'] = treater.username
        validated_data['commiter'] = commiter.username
        instance = self.Meta.model.objects.create(**validated_data)
        instance.users.add(treater, commiter)
        return instance

class DbSerializer(serializers.ModelSerializer):

    class Meta:
        model = Dbconf
        fields = '__all__'

    def create(self, validated_data):
        password = validated_data.get('password', None)
        pc = prpcrypt()
        validated_data['password'] = pc.encrypt(password)
        instance = self.Meta.model.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        password = validated_data.get('password', None)
        if password != instance.password:
            pc = prpcrypt()
            validated_data['password'] = pc.encrypt(password)
        self.Meta.model.objects.filter(id=instance.id).update(**validated_data)
        return instance
