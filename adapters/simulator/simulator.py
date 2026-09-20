"""
UniTransit - Multi-Modal Transport Telemetry Simulator Engine
Generates realistic high-concurrency GPS telemetry, speed changes, stops,
delays, route deviations, and network failure simulations.
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import os
import random
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

# Enable relative import of common event schema
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from adapters.common.event_schema import (
    NormalizedTransportEvent,
    OccupancyStatus,
    TransportMode,
    VehicleStatus,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (Simulator) %(message)s",
)
logger = logging.getLogger("unitransit.simulator")

# Canonical simulation routes (Waypoints: [lat, lon])
CORRIDORS: Dict[str, List[Tuple[float, float]]] = {
    "ROUTE-12": [
        (12.9716, 80.2440),
        (12.9750, 80.2460),
        (12.9800, 80.2480),
        (12.9840, 80.2505),
        (12.9880, 80.2530),
        (12.9920, 80.2565),
        (12.9960, 80.2600),
        (13.0000, 80.2625),
        (13.0040, 80.2650),
    ],
    "ROUTE-METRO-BLUE": [
        (12.9900, 80.1700),
        (13.0000, 80.1850),
        (13.0100, 80.2000),
        (13.0200, 80.2150),
        (13.0300, 80.2300),
        (13.0450, 80.2500),
        (13.0600, 80.2700),
    ],
    "ROUTE-FERRY-01": [
        (13.0850, 80.2950),
        (13.0950, 80.3020),
        (13.1050, 80.3080),
        (13.1200, 80.3150),
    ],
}


def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates compass heading bearing in degrees (0 - 360)."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_lambda = math.radians(lon2 - lon1)
    y = math.sin(delta_lambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda)
    bearing = math.degrees(math.atan2(y, x))
    return (bearing + 360) % 360


@dataclass
class SimulatedVehicleState:
    vehicle_id: str
    mode: str
    route_id: str
    waypoints: List[Tuple[float, float]]
    current_index: int = 0
    sub_progress: float = 0.0  # 0.0 to 1.0 between current waypoint and next
    speed: float = 35.0  # km/h
    heading: float = 0.0
    status: str = VehicleStatus.MOVING.value
    delay_seconds: int = 0
    dwell_remaining: int = 0  # Stop dwell ticks
    direction: int = 1  # 1 forward, -1 backward along waypoints
    is_offline: bool = False

    def step(self, interval_sec: float, fault_rate: float) -> Optional[NormalizedTransportEvent]:
        # Simulated connection drop
        if random.random() < fault_rate * 0.2:
            self.is_offline = not self.is_offline
            if self.is_offline:
                return None  # Packet dropped / simulated connection failure

        # If currently dwelling at a stop
        if self.dwell_remaining > 0:
            self.dwell_remaining -= 1
            self.status = VehicleStatus.STOPPED.value
            self.speed = 0.0
            p1 = self.waypoints[self.current_index]
            return NormalizedTransportEvent(
                vehicle_id=self.vehicle_id,
                mode=self.mode,
                route_id=self.route_id,
                latitude=round(p1[0], 6),
                longitude=round(p1[1], 6),
                speed=0.0,
                heading=round(self.heading, 1),
                status=VehicleStatus.STOPPED.value,
                delay_seconds=self.delay_seconds,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

        # Fault Injection
        is_overspeed_fault = random.random() < fault_rate * 0.15
        is_unexpected_stop_fault = random.random() < fault_rate * 0.15
        is_route_deviation_fault = random.random() < fault_rate * 0.15

        if is_unexpected_stop_fault:
            self.status = VehicleStatus.STOPPED.value
            self.speed = 0.0
            self.dwell_remaining = random.randint(2, 6)
            self.delay_seconds += int(interval_sec * self.dwell_remaining)
        elif is_overspeed_fault:
            self.status = VehicleStatus.MOVING.value
            self.speed = random.uniform(85.0, 110.0)  # Overspeed anomaly
        else:
            self.status = VehicleStatus.MOVING.value
            target_speed = 45.0 if self.mode == "bus" else 75.0 if self.mode == "metro" else 25.0
            self.speed = max(15.0, min(80.0, self.speed + random.uniform(-4.0, 4.0)))

        # Movement physics along polyline
        idx = self.current_index
        next_idx = idx + self.direction
        if next_idx >= len(self.waypoints):
            self.direction = -1
            next_idx = idx - 1
            self.dwell_remaining = 3
        elif next_idx < 0:
            self.direction = 1
            next_idx = idx + 1
            self.dwell_remaining = 3

        p1 = self.waypoints[idx]
        p2 = self.waypoints[next_idx]

        # Calculate step distance (speed km/h -> km/sec -> rough coordinate delta)
        km_moved = (self.speed / 3600.0) * interval_sec
        # Approximate 1 deg lat ~ 111 km
        progress_increment = km_moved / 0.8  # ~ 800m between waypoints
        self.sub_progress += progress_increment

        if self.sub_progress >= 1.0:
            self.sub_progress = 0.0
            self.current_index = next_idx
            # Chance of stopping at designated waypoint station
            if random.random() < 0.4:
                self.dwell_remaining = 2
            p1 = p2

        cur_lat = p1[0] + (p2[0] - p1[0]) * self.sub_progress
        cur_lon = p1[1] + (p2[1] - p1[1]) * self.sub_progress

        # Injected Route Deviation Fault
        if is_route_deviation_fault:
            cur_lat += random.uniform(-0.015, 0.015)
            cur_lon += random.uniform(-0.015, 0.015)

        self.heading = calculate_bearing(p1[0], p1[1], p2[0], p2[1])

        return NormalizedTransportEvent(
            vehicle_id=self.vehicle_id,
            mode=self.mode,
            route_id=self.route_id,
            latitude=round(cur_lat, 6),
            longitude=round(cur_lon, 6),
            speed=round(self.speed, 1),
            heading=round(self.heading, 1),
            status=self.status,
            occupancy_status=OccupancyStatus.MANY_SEATS_AVAILABLE.value,
            delay_seconds=self.delay_seconds,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )


class TransportSimulator:
    def __init__(
        self,
        vehicle_count: int = 25,
        interval: float = 2.0,
        fault_rate: float = 0.02,
        mode: str = "bus",
        redis_host: str = "localhost",
        redis_port: int = 6379,
        stream_key: str = "transport.events",
        dry_run: bool = False,
        event_rate: Optional[float] = None,
    ):
        self.vehicle_count = vehicle_count
        self.interval = interval
        self.fault_rate = fault_rate
        self.mode = mode
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.stream_key = stream_key
        self.dry_run = dry_run
        self.event_rate = event_rate
        self.redis_client = None
        self.vehicles: List[SimulatedVehicleState] = []
        self._init_fleet()

    def _init_fleet(self):
        corridor_keys = list(CORRIDORS.keys())
        for i in range(1, self.vehicle_count + 1):
            route_key = corridor_keys[i % len(corridor_keys)]
            waypoints = CORRIDORS[route_key]
            v_mode = "bus" if "12" in route_key else "metro" if "METRO" in route_key else "ferry"
            v = SimulatedVehicleState(
                vehicle_id=f"{v_mode.upper()}-{100 + i}",
                mode=v_mode,
                route_id=route_key,
                waypoints=waypoints,
                current_index=random.randint(0, len(waypoints) - 1),
                sub_progress=random.random(),
                speed=random.uniform(25.0, 50.0),
                heading=random.uniform(0.0, 360.0),
            )
            self.vehicles.append(v)

    def connect_redis(self) -> bool:
        if self.dry_run:
            logger.info("Simulator running in DRY-RUN mode (No Redis required).")
            return True
        try:
            import redis

            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                decode_responses=True,
                socket_connect_timeout=2.0,
            )
            self.redis_client.ping()
            logger.info(f"Connected to Redis broker at {self.redis_host}:{self.redis_port}")
            return True
        except Exception as e:
            logger.warning(f"Could not connect to Redis at {self.redis_host}:{self.redis_port}: {e}. Falling back to dry-run mode.")
            self.dry_run = True
            return False

    def publish_event(self, event: NormalizedTransportEvent) -> Optional[str]:
        if self.dry_run or not self.redis_client:
            return None
        payload = event.to_dict()
        msg_id = self.redis_client.xadd(
            self.stream_key,
            {"event": json.dumps(payload)},
            maxlen=50000,
            approximate=True,
        )
        try:
            from common.metrics import EVENTS_PUBLISHED_TOTAL
            mode_str = event.mode.value if hasattr(event.mode, "value") else str(event.mode)
            EVENTS_PUBLISHED_TOTAL.labels(mode=mode_str, source="simulator").inc()
        except Exception:
            pass
        return msg_id

    def run(self, duration_sec: Optional[float] = None):
        self.connect_redis()
        logger.info(
            f"Starting UniTransit Simulator: {self.vehicle_count} vehicles, "
            f"interval={self.interval}s, fault_rate={self.fault_rate * 100:.1f}%, mode={self.mode}"
        )

        start_time = time.time()
        ticks = 0
        total_events = 0

        try:
            while True:
                tick_start = time.time()
                events_this_tick = 0

                for veh in self.vehicles:
                    event = veh.step(self.interval, self.fault_rate)
                    if event:
                        self.publish_event(event)
                        events_this_tick += 1
                        total_events += 1

                ticks += 1
                elapsed = time.time() - tick_start
                sleep_time = max(0.0, self.interval - elapsed)

                if ticks % 5 == 0 or self.dry_run:
                    eps = events_this_tick / max(0.001, elapsed)
                    logger.info(
                        f"Tick #{ticks} | Active: {events_this_tick}/{self.vehicle_count} | "
                        f"Total Produced: {total_events} | Throughput: {eps:.1f} evt/sec"
                    )

                if duration_sec and (time.time() - start_time) >= duration_sec:
                    logger.info(f"Completed requested duration of {duration_sec}s. Exiting simulator.")
                    break

                time.sleep(sleep_time)

        except KeyboardInterrupt:
            logger.info("Simulator gracefully stopped by user.")


def main():
    parser = argparse.ArgumentParser(description="UniTransit Multi-Modal Real-Time Transport Telemetry Simulator")
    parser.add_argument("--vehicles", type=int, default=25, help="Number of vehicles to simulate (e.g. 100, 1000, 10000)")
    parser.add_argument("--interval", type=float, default=2.0, help="Telemetry update interval in seconds")
    parser.add_argument("--fault-rate", type=float, default=0.02, help="Fault injection rate (0.0 to 1.0)")
    parser.add_argument("--mode", type=str, default="bus", help="Default vehicle transport mode")
    parser.add_argument("--redis-host", type=str, default=os.getenv("REDIS_HOST", "localhost"), help="Redis host")
    parser.add_argument("--redis-port", type=int, default=int(os.getenv("REDIS_PORT", 6379)), help="Redis port")
    parser.add_argument("--stream", type=str, default="transport.events", help="Redis stream key")
    parser.add_argument("--dry-run", action="store_true", help="Run without live Redis broker")
    parser.add_argument("--duration", type=float, default=None, help="Duration in seconds to run")
    parser.add_argument("--event-rate", type=float, default=None, help="Target events per second throttle rate")

    args = parser.parse_args()

    sim = TransportSimulator(
        vehicle_count=args.vehicles,
        interval=args.interval,
        fault_rate=args.fault_rate,
        mode=args.mode,
        redis_host=args.redis_host,
        redis_port=args.redis_port,
        stream_key=args.stream,
        dry_run=args.dry_run,
        event_rate=args.event_rate,
    )
    sim.run(duration_sec=args.duration)


if __name__ == "__main__":
    main()
