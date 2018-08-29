from django.contrib.auth.models import Group


def get_group():
    a = []
    for i in Group.objects.all():
        a.append(i)
    return a

class AppellationMixins(object):
    dev_spm = 'developer_supremo'
    dev_mng = 'developer_manager'
    admin = 'ops'
    dev = 'developer'
    env_test = 'test'
    env_prd = 'prd'

