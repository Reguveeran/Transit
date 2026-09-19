"""
Management command to search and import transit routes and stops
from the global Transitland v2 platform directly into the local UniTransit database.
"""

from django.core.management.base import BaseCommand
from adapters.gtfs_realtime.transitland_adapter import TransitlandAdapter
from apps.routes.models import Route
from apps.vehicles.models import TransportMode


class Command(BaseCommand):
    help = "Imports real-world transit agency routes and stops using Transitland v2."

    def add_arguments(self, parser):
        parser.add_argument("--search", type=str, default="Ferry", help="Search keyword for transit agency")
        parser.add_argument("--limit", type=int, default=5, help="Number of routes to import")

    def handle(self, *args, **options):
        search_query = options["search"]
        limit = options["limit"]

        self.stdout.write(self.style.NOTICE(f"🔍 Searching Transitland for operators matching '{search_query}'..."))
        adapter = TransitlandAdapter()

        try:
            operators = adapter.get_operators(search=search_query, limit=3)
            if not operators:
                self.stdout.write(self.style.WARNING(f"No operators found for '{search_query}'."))
                return

            op = operators[0]
            op_id = op.get("onestop_id")
            op_name = op.get("name")
            self.stdout.write(self.style.SUCCESS(f"Found Operator: {op_name} ({op_id})"))

            self.stdout.write(self.style.NOTICE(f"Fetching routes for {op_name}..."))
            routes = adapter.get_routes(operator_onestop_id=op_id, limit=limit)

            mode_obj, _ = TransportMode.objects.get_or_create(
                name="ferry" if "ferry" in op_name.lower() else "bus",
                defaults={"display_name": op_name, "icon_name": "ship" if "ferry" in op_name.lower() else "bus"}
            )

            count = 0
            for r in routes:
                r_id = r.get("onestop_id") or f"TL-{r.get('id')}"
                s_name = r.get("route_short_name") or r.get("route_long_name") or r_id
                l_name = r.get("route_long_name") or s_name
                color = f"#{r.get('route_color', '10B981').replace('#', '')}"

                _, created = Route.objects.get_or_create(
                    route_id=r_id,
                    defaults={
                        "short_name": s_name[:30],
                        "long_name": l_name[:255],
                        "transport_mode": mode_obj,
                        "color": color,
                        "is_active": True,
                    }
                )
                status_str = "Created" if created else "Existing"
                self.stdout.write(f"  • [{status_str}] Route: {s_name} - {l_name} ({r_id})")
                count += 1

            self.stdout.write(self.style.SUCCESS(f"✅ Successfully synchronized {count} routes from {op_name} into UniTransit DB!"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Transitland import error: {e}"))
