#coding=utf8
from django.forms.models import model_to_dict
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.exceptions import ParseError
from utils.baseviews import ReturnFormatMixin, BaseView
from .serializers import *
from .models import *
from utils.basemixins import AppellationMixins
from .mixins import PromptMxins, ActionMxins
from utils.permissions import AuthOrReadOnly
from utils import inception
import re
from rest_framework import permissions

class InceptionMainView(PromptMxins, ActionMxins, BaseView):
    serializer_class = InceptionSerializer
    permission_classes = [AuthOrReadOnly]
    action_type = '--enable-execute'

    def get_queryset(self):
        userobj = self.request.user
        if userobj.is_superuser:  # 管理员
            return Inceptsql.objects.all()
        return userobj.groups.first().inceptsql_set.all() if  userobj.groups.first() == self.dev_spm else userobj.inceptsql_set.all()

    @detail_route()
    def execute(self, request, *args, **kwargs):
        sqlobj = Inceptsql.objects.get(pk = kwargs.get('pk'))
        # 执行SQL（防止同一个SQL被人已执行了，这边还没刷新 但点了执行，产生bug。执行前先检查status）
        if sqlobj.status != -1:
            self.ret = {'status': -2, 'msg':self.executed}
            return Response(self.ret)
        affected_rows = 0
        execute_time = 0
        opids = []
        success_sqls, exception_sqls = self.check_execute_sql(sqlobj.db.id, sqlobj.sql_content)
        for success_sql in success_sqls:
            sqlobj.status = 0
            # 执行结果，受影响的条数，执行所耗时间，回滚语句
            sqlobj.rollback_db = success_sql[8]
            affected_rows += success_sql[6]
            execute_time += float(success_sql[9])
            opids.append(success_sql[7].replace("'", ""))  # execute_sql[7].replace("'","")  : 每条sql执行后的回滚opid
        if exception_sqls:
            sqlobj.status = 2
            sqlobj.execute_errors = exception_sqls
            self.ret['status'] = -1
        sqlobj.rollback_opid = opids
        sqlobj.exe_affected_rows = affected_rows
        self.ret['data']['affected_rows'] = affected_rows
        self.ret['data']['execute_time'] = '%.3f' % execute_time # 保留3位小数
        self.ret['msg'] = exception_sqls
        # self.mail(sqlobj, self.action_type)
        self.replace_remark(sqlobj)
        return Response(self.ret)

    @detail_route()
    def reject(self, request, *args, **kwargs):
        sqlobj = Inceptsql.objects.get(pk = kwargs.get('pk'))
        sqlobj.status = 1
        self.replace_remark(sqlobj)
        return Response(self.ret)

    @detail_route()
    def rollback(self, request, *args, **kwargs):
        sqlobj = Inceptsql.objects.get(pk = kwargs.get('pk'))
        dbobj = sqlobj.db
        rollback_opid_list = sqlobj.rollback_opid
        rollback_db = sqlobj.rollback_db  # 回滚库
        # 拼接回滚语句
        back_sqls = ''  # 回滚语句
        for opid in eval(rollback_opid_list)[1:]:
            # 1 从回滚总表中获取表名
            back_source = 'select tablename from $_$Inception_backup_information$_$ where opid_time = "{}" '.format(opid)
            back_table = inception.get_rollback(back_source, rollback_db)[0][0]
            # 2 从回滚子表中获取回滚语句
            back_content = 'select rollback_statement from {}.{} where opid_time = "{}" '.format(rollback_db, back_table, opid)
            per_rollback = inception.get_rollback(back_content)  # 获取回滚数据
            for i in per_rollback:  # 累加拼接
                back_sqls += i[0]
        # 拼接回滚语句 执行回滚操作，修改sql状态
        db_addr = self.get_db_addr(dbobj.user, dbobj.password, dbobj.host, dbobj.port, self.action_type)
        execute_results = inception.table_structure(db_addr, dbobj.name, back_sqls).get('result')
        sqlobj.status = -3
        sqlobj.roll_affected_rows = self.ret['data']['affected_rows'] = len(execute_results) - 1  # 执行回滚语句的结果，除去第一个use 数据库的
        self.replace_remark(sqlobj)
        return Response(self.ret)

class InceptionCheckView(PromptMxins, ActionMxins, BaseView):
    queryset = Inceptsql.objects.all()
    forbidden_word_list = ['use ', 'drop ']
    action_type = '--enable-check'
    serializer_class = InceptionSerializer

    def get_forbidden_words(self, sql_content):
        forbidden_words = [fword for fword in self.forbidden_word_list if re.search(re.compile(fword, re.I), sql_content)]
        if forbidden_words:
            raise ParseError({self.forbidden_words: forbidden_words})

    def check_user_group(self, request):
        if request.data.get('env') == self.env_prd and not request.user.is_superuser:
            if not request.user.groups.exists():
                raise ParseError(self.not_exists_group)
            return request.user.groups.first().id

    def create(self, request, *args, **kwargs):
        request_data = request.data
        request_data['group_id'] = self.check_user_group(request)
        serializer = self.serializer_class(data = request_data)
        serializer.is_valid(raise_exception = True)
        sql_content = request_data.get('sql_content')
        db_id = request_data.get('db')
        # 禁止词过滤
        self.get_forbidden_words(sql_content)
        # sql合法性检查
        self.check_execute_sql(db_id, sql_content)
        # 审核通过，写入数据库
        request_data['commiter'] = request.user
        sqlobj = serializer.create(request_data)
        print(request_data)
        print(sqlobj)
        print(self.ret)
        # self.mail(sqlobj, self.action_type)
        return Response(self.ret)

class SelectDataView(ReturnFormatMixin, AppellationMixins, APIView):
    def post(self, request):  # 前端切换环境时，返回相应的数据（执行人，数据库名）
        request_data = request.data
        env = request_data.get('env')
        self.ret['data']['dbs'] = [model_to_dict(db, fields=['id', 'name']) for db in Dbconf.objects.filter(env = env)]
        userobj = request.user
        if userobj.is_superuser or env == self.env_test or userobj.groups.first() != self.dev:  # 超级用户 or 测试环境 or 除开发外，执行人是自己
            managers = [userobj.username]
        else:
            ug = userobj.groups.first()
            managers = [u.username for u in ug.user_set.all() if u.groups.first() == self.dev_mng] if ug else []
        self.ret['data']['managers'] = managers
        return Response(self.ret)


class DbViewSet(BaseView):
    permission_classes = (permissions.IsAuthenticated, permissions.DjangoObjectPermissions)
    queryset = Dbconf.objects.all()
    serializer_class = DbSerializer
    search_fields = ['name','host','port','user','password']

