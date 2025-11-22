from rest_framework.routers import DefaultRouter
from .views import (
    PackageViewSet,
    PackageCategoryViewSet,
    PackageCategoryItemViewSet,
)

router = DefaultRouter()
router.register(r'packages', PackageViewSet, basename='package')
router.register(r'package-categories', PackageCategoryViewSet, basename='package-category')
router.register(r'package-items', PackageCategoryItemViewSet, basename='package-category-item')

urlpatterns = router.urls
