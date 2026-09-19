from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.alerts.models import Alert, ServiceAlert
from apps.alerts.serializers import AlertSerializer, ServiceAlertSerializer


class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.select_related("vehicle", "route").all()
    serializer_class = AlertSerializer
    lookup_field = "alert_id"
    filterset_fields = ["alert_type", "severity", "is_resolved", "vehicle__vehicle_id"]
    ordering_fields = ["created_at", "severity"]


class ServiceAlertViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ServiceAlert.objects.prefetch_related("affected_routes").filter(is_active=True)
    serializer_class = ServiceAlertSerializer
    lookup_field = "alert_id"
