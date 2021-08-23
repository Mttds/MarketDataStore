from rest_framework import routers
from .views import EquitiesViewSet

router = routers.SimpleRouter()
router.register('', EquitiesViewSet)
urlpatterns = router.urls