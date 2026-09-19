from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.alerts.views import AlertViewSet, ServiceAlertViewSet

router = DefaultRouter()
router.register(r"service", ServiceAlertViewSet, basename="servicealert")
router.register(r"", AlertViewSet, basename="alert")

urlpatterns = [
    path("", include(router.urls)),
]
