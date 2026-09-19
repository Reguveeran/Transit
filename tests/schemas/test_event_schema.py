import unittest
from adapters.common.event_schema import (
    NormalizedTransportEvent,
    OccupancyStatus,
    SchemaValidationError,
    TransportMode,
    VehicleStatus,
)


class TestNormalizedTransportEvent(unittest.TestCase):
    def test_valid_event_creation(self):
        event = NormalizedTransportEvent(
            vehicle_id="BUS-101",
            mode="bus",
            route_id="R12",
            latitude=12.9716,
            longitude=80.2440,
            speed=42.0,
            heading=180.0,
            status="MOVING",
            timestamp="2026-09-19T18:30:00Z",
        )
        self.assertEqual(event.vehicle_id, "BUS-101")
        self.assertEqual(event.mode, "bus")
        self.assertEqual(event.status, "MOVING")
        self.assertIsNotNone(event.event_id)

    def test_enum_modes_and_statuses(self):
        event = NormalizedTransportEvent(
            vehicle_id="METRO-404",
            mode=TransportMode.METRO,
            route_id="BLUE-LINE",
            latitude=13.0827,
            longitude=80.2707,
            speed=60.0,
            heading=90.0,
            status=VehicleStatus.BOARDING,
            occupancy_status=OccupancyStatus.STANDING_ROOM_ONLY,
            timestamp="2026-09-19T18:30:00Z",
        )
        self.assertEqual(event.mode, "metro")
        self.assertEqual(event.status, "BOARDING")
        self.assertEqual(event.occupancy_status, "STANDING_ROOM_ONLY")

    def test_serialization_to_dict_and_json(self):
        event = NormalizedTransportEvent.create_sample(vehicle_id="FERRY-99", mode="ferry")
        data_dict = event.to_dict()
        self.assertIn("vehicle_id", data_dict)
        self.assertEqual(data_dict["vehicle_id"], "FERRY-99")

        json_str = event.to_json()
        reconstructed = NormalizedTransportEvent.from_json(json_str)
        self.assertEqual(reconstructed.vehicle_id, event.vehicle_id)
        self.assertEqual(reconstructed.latitude, event.latitude)

    def test_invalid_coordinates(self):
        with self.assertRaises(SchemaValidationError):
            NormalizedTransportEvent(
                vehicle_id="BUS-101",
                mode="bus",
                route_id="R12",
                latitude=95.0,  # Invalid: > 90
                longitude=80.2440,
                speed=42.0,
                heading=180.0,
                status="MOVING",
                timestamp="2026-09-19T18:30:00Z",
            )

    def test_negative_speed(self):
        with self.assertRaises(SchemaValidationError):
            NormalizedTransportEvent(
                vehicle_id="BUS-101",
                mode="bus",
                route_id="R12",
                latitude=12.9716,
                longitude=80.2440,
                speed=-5.0,  # Invalid: negative
                heading=180.0,
                status="MOVING",
                timestamp="2026-09-19T18:30:00Z",
            )

    def test_invalid_mode(self):
        with self.assertRaises(SchemaValidationError):
            NormalizedTransportEvent(
                vehicle_id="BUS-101",
                mode="spacecraft",  # Invalid mode
                route_id="R12",
                latitude=12.9716,
                longitude=80.2440,
                speed=20.0,
                heading=180.0,
                status="MOVING",
                timestamp="2026-09-19T18:30:00Z",
            )

    def test_invalid_timestamp_format(self):
        with self.assertRaises(SchemaValidationError):
            NormalizedTransportEvent(
                vehicle_id="BUS-101",
                mode="bus",
                route_id="R12",
                latitude=12.9716,
                longitude=80.2440,
                speed=20.0,
                heading=180.0,
                status="MOVING",
                timestamp="invalid-timestamp-string",
            )


if __name__ == "__main__":
    unittest.main()
