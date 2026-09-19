from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Avg, Count, Max, Min
from apps.vehicles.models import Vehicle, TransportMode
from apps.analytics.models import DelayAnalytics, FleetStats
from apps.analytics.serializers import DelayAnalyticsSerializer, FleetStatsSerializer


class VehicleAnalyticsView(APIView):
    """GET /api/v1/analytics/vehicles - Fleet breakdown by mode, speed, and active counts."""

    def get(self, request):
        modes = TransportMode.objects.all()
        breakdown = []
        for m in modes:
            vehs = Vehicle.objects.filter(transport_mode=m)
            total = vehs.count()
            active = vehs.filter(status="MOVING").count()
            avg_spd = vehs.aggregate(Avg("current_speed"))["current_speed__avg"] or 0.0
            breakdown.append(
                {
                    "mode": m.name,
                    "display_name": m.display_name,
                    "total_vehicles": total,
                    "active_vehicles": active,
                    "average_speed_kmh": round(avg_spd, 1),
                }
            )

        total_all = Vehicle.objects.count()
        active_all = Vehicle.objects.filter(status="MOVING").count()
        overall_avg_speed = Vehicle.objects.aggregate(Avg("current_speed"))["current_speed__avg"] or 0.0

        return Response(
            {
                "summary": {
                    "total_vehicles": total_all,
                    "active_vehicles": active_all,
                    "overall_average_speed": round(overall_avg_speed, 1),
                },
                "breakdown": breakdown,
            }
        )


class DelayAnalyticsView(APIView):
    """GET /api/v1/analytics/delays - Delay metrics grouped by route."""

    def get(self, request):
        analytics = DelayAnalytics.objects.select_related("route").all()
        serializer = DelayAnalyticsSerializer(analytics, many=True)
        return Response(serializer.data)
