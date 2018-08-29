from rest_framework.routers import DefaultRouter
from .views import WorkOrderViewset

workorder_router = DefaultRouter()
workorder_router.register(r'workorder', WorkOrderViewset, base_name="workorder")