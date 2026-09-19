from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.routes.views import RouteViewSet

router = DefaultRouter()
router.register(r"", RouteViewSet, basename="route")

urlpatterns = [
    path("", include(router.urls)),
]
