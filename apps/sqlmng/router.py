from rest_framework.routers import DefaultRouter
from .views import InceptionCheckView,InceptionMainView,DbViewSet,SelectDataView


sqlmng_router = DefaultRouter()
sqlmng_router.register(r'dbconfs', DbViewSet)
sqlmng_router.register(r'inceptions', InceptionMainView, base_name='Inceptionmainview')
sqlmng_router.register(r'inceptioncheck', InceptionCheckView, base_name='Inceptioncheckview')


