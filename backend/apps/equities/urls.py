from django.urls import include, path
from rest_framework_nested import routers
from .views import EquitiesViewSet, EquityDividendsViewSet

# equities endpoint
router = routers.SimpleRouter()
router.register('', EquitiesViewSet)

# dividends nested router /equities/:id/dividends
dividends_router = routers.NestedSimpleRouter(router, '', lookup='equity')
dividends_router.register('dividends', EquityDividendsViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include(dividends_router.urls))
]