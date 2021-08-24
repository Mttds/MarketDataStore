from rest_framework import routers
from .views import DividendsViewSet

router = routers.SimpleRouter()
router.register('', DividendsViewSet)
urlpatterns = router.urls