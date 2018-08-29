# -*- coding: utf-8 -*-
from django.db import models
from users.models import User

# Create your models here.


class WorkOrder(models.Model):
    TYPE = (
        (0, '数据库'),
        (1, 'WEB服务'),
        (2, '计划任务'),
        (3, '配置文件'),
        (4, '其它'),
    )
    STATUS = (
        (0, '申请'),
        (1, '处理中'),
        (2, '完成'),
        (3, '失败'),
    )
    title = models.CharField(max_length=100, verbose_name=u'工单标题')
    type = models.IntegerField(choices=TYPE, default=0, verbose_name=u'工单类型')
    order_contents = models.TextField(verbose_name='工单内容')
    applicant = models.ForeignKey(User, verbose_name=u'申请人', related_name='work_order_applicant')
    assign_to = models.ForeignKey(User, verbose_name=u'指派给')
    final_processor = models.ForeignKey(User, null=True, blank=True, verbose_name=u'最终处理人', related_name='final_processor')
    status = models.IntegerField(choices=STATUS, default=0, verbose_name=u'工单状态')
    result_desc = models.TextField(verbose_name=u'处理结果', blank=True, null=True)
    apply_time = models.DateTimeField(auto_now_add=True, verbose_name=u'申请时间')
    complete_time = models.DateTimeField(auto_now=True, verbose_name=u'处理完成时间')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '工单'
        verbose_name_plural = verbose_name
        ordering = ['-complete_time']

