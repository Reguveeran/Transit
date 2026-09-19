from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.routes.models import Route
from apps.routes.serializers import RouteSerializer
from apps.vehicles.serializers import VehicleSerializer


class RouteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Route.objects.select_related("transport_mode").all()
    serializer_class = RouteSerializer
    lookup_field = "route_id"
    filterset_fields = ["is_active", "transport_mode__name"]
    search_fields = ["route_id", "short_name", "long_name"]
    ordering_fields = ["short_name", "route_id"]

    @action(detail=True, methods=["get"])
    def vehicles(self, request, route_id=None):
        route = self.get_object()
        active_vehicles = route.active_vehicles.all()
        serializer = VehicleSerializer(active_vehicles, many=True)
        return Response(serializer.data)
