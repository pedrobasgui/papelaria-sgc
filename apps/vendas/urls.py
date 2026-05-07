from rest_framework.routers import DefaultRouter
from .views import VendaViewSet

router = DefaultRouter()
router.register(r"", VendaViewSet, basename="venda")

urlpatterns = router.urls
