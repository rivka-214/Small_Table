from rest_framework.routers import DefaultRouter

from .views import AddonCategoryViewSet, AddonViewSet

router = DefaultRouter()
router.register(r'addon-categories', AddonCategoryViewSet, basename='addon-category')
router.register(r'addons', AddonViewSet, basename='addon')

urlpatterns = router.urls
