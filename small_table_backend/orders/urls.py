from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import OrderViewSet, OrderAddonViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-addons', OrderAddonViewSet, basename='order-addon')

urlpatterns = [
    path('', include(router.urls)),
]
