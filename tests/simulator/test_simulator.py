import unittest
from adapters.simulator.simulator import (
    TransportSimulator,
    SimulatedVehicleState,
    calculate_bearing,
    CORRIDORS,
)
from adapters.common.event_schema import NormalizedTransportEvent


class TestTransportSimulator(unittest.TestCase):
    def test_calculate_bearing(self):
        # Heading due North (lat increases, lon unchanged)
        bearing_north = calculate_bearing(10.0, 80.0, 11.0, 80.0)
        self.assertAlmostEqual(bearing_north, 0.0, delta=1.0)

        # Heading due East (lat unchanged, lon increases)
        bearing_east = calculate_bearing(10.0, 80.0, 10.0, 81.0)
        self.assertAlmostEqual(bearing_east, 90.0, delta=1.0)

    def test_simulator_fleet_initialization(self):
        sim = TransportSimulator(vehicle_count=100, dry_run=True)
        self.assertEqual(len(sim.vehicles), 100)
        self.assertTrue(sim.vehicles[0].vehicle_id.startswith(("BUS-", "METRO-", "FERRY-")))

    def test_vehicle_state_step_produces_valid_event(self):
        state = SimulatedVehicleState(
            vehicle_id="BUS-TEST",
            mode="bus",
            route_id="ROUTE-12",
            waypoints=CORRIDORS["ROUTE-12"],
            speed=40.0,
        )
        event = state.step(interval_sec=2.0, fault_rate=0.0)
        self.assertIsNotNone(event)
        self.assertIsInstance(event, NormalizedTransportEvent)
        self.assertEqual(event.vehicle_id, "BUS-TEST")
        self.assertGreaterEqual(event.latitude, 12.0)
        self.assertLessEqual(event.latitude, 14.0)

    def test_fault_rate_simulation(self):
        # High fault rate should occasionally generate faults (e.g. overspeed or offline)
        state = SimulatedVehicleState(
            vehicle_id="BUS-FAULT-TEST",
            mode="bus",
            route_id="ROUTE-12",
            waypoints=CORRIDORS["ROUTE-12"],
            speed=40.0,
        )
        events = []
        for _ in range(50):
            ev = state.step(interval_sec=1.0, fault_rate=0.8)
            if ev:
                events.append(ev)

        # Some events should have high speed or stopped states
        speeds = [e.speed for e in events]
        self.assertTrue(any(s > 80.0 or s == 0.0 for s in speeds))

    def test_simulator_dry_run_execution(self):
        sim = TransportSimulator(vehicle_count=10, interval=0.1, dry_run=True)
        # Run for 0.3 seconds and verify termination without errors
        sim.run(duration_sec=0.3)
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
