"""
UniTransit - Common Normalized Transport Event Schema
Provides data models, enums, validation, and JSON serialization.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional, Union


class TransportMode(str, Enum):
    BUS = "bus"
    TRAIN = "train"
    METRO = "metro"
    TRAM = "tram"
    FERRY = "ferry"
    AIRCRAFT = "aircraft"


class VehicleStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    BOARDING = "BOARDING"
    MOVING = "MOVING"
    STOPPED = "STOPPED"
    CONGESTED = "CONGESTED"
    OFFLINE = "OFFLINE"
    EMERGENCY = "EMERGENCY"


class OccupancyStatus(str, Enum):
    EMPTY = "EMPTY"
    MANY_SEATS_AVAILABLE = "MANY_SEATS_AVAILABLE"
    FEW_SEATS_AVAILABLE = "FEW_SEATS_AVAILABLE"
    STANDING_ROOM_ONLY = "STANDING_ROOM_ONLY"
    FULL = "FULL"
    NOT_ACCEPTING_PASSENGERS = "NOT_ACCEPTING_PASSENGERS"


class SchemaValidationError(ValueError):
    """Raised when an incoming event violates canonical transport.event.v1 specification."""
    pass


@dataclass
class NormalizedTransportEvent:
    vehicle_id: str
    mode: Union[TransportMode, str]
    route_id: str
    latitude: float
    longitude: float
    speed: float
    heading: float
    status: Union[VehicleStatus, str]
    timestamp: str  # ISO 8601 UTC string
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trip_id: Optional[str] = None
    occupancy_status: Optional[Union[OccupancyStatus, str]] = OccupancyStatus.MANY_SEATS_AVAILABLE.value
    delay_seconds: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.validate()

    def validate(self) -> None:
        if not self.vehicle_id or not isinstance(self.vehicle_id, str):
            raise SchemaValidationError("vehicle_id must be a non-empty string.")

        # Validate mode
        valid_modes = {m.value for m in TransportMode}
        mode_val = self.mode.value if isinstance(self.mode, TransportMode) else str(self.mode)
        if mode_val.lower() not in valid_modes:
            raise SchemaValidationError(f"Invalid mode '{self.mode}'. Must be one of: {valid_modes}")
        self.mode = mode_val.lower()

        if not self.route_id or not isinstance(self.route_id, str):
            raise SchemaValidationError("route_id must be a non-empty string.")

        # Validate coordinates
        try:
            lat = float(self.latitude)
            lon = float(self.longitude)
        except (ValueError, TypeError):
            raise SchemaValidationError("latitude and longitude must be valid float numbers.")

        if not (-90.0 <= lat <= 90.0):
            raise SchemaValidationError(f"latitude {lat} out of bounds [-90.0, 90.0].")
        if not (-180.0 <= lon <= 180.0):
            raise SchemaValidationError(f"longitude {lon} out of bounds [-180.0, 180.0].")
        self.latitude = lat
        self.longitude = lon

        # Validate speed and heading
        try:
            spd = float(self.speed)
            hdg = float(self.heading)
        except (ValueError, TypeError):
            raise SchemaValidationError("speed and heading must be valid float numbers.")

        if spd < 0.0:
            raise SchemaValidationError(f"speed {spd} cannot be negative.")
        if not (0.0 <= hdg <= 360.0):
            raise SchemaValidationError(f"heading {hdg} must be between 0.0 and 360.0 degrees.")
        self.speed = spd
        self.heading = hdg

        # Validate status
        valid_statuses = {s.value for s in VehicleStatus}
        status_val = self.status.value if isinstance(self.status, VehicleStatus) else str(self.status)
        if status_val.upper() not in valid_statuses:
            raise SchemaValidationError(f"Invalid status '{self.status}'. Must be one of: {valid_statuses}")
        self.status = status_val.upper()

        # Validate timestamp
        if not isinstance(self.timestamp, str):
            raise SchemaValidationError("timestamp must be an ISO 8601 formatted string.")
        try:
            # Verify parses as ISO format
            iso_str = self.timestamp.replace("Z", "+00:00")
            datetime.fromisoformat(iso_str)
        except Exception as e:
            raise SchemaValidationError(f"Invalid ISO 8601 timestamp '{self.timestamp}': {e}")

        # Validate occupancy if present
        if self.occupancy_status is not None:
            valid_occ = {o.value for o in OccupancyStatus}
            occ_val = self.occupancy_status.value if isinstance(self.occupancy_status, OccupancyStatus) else str(self.occupancy_status)
            if occ_val.upper() not in valid_occ:
                raise SchemaValidationError(f"Invalid occupancy_status '{self.occupancy_status}'. Must be one of: {valid_occ}")
            self.occupancy_status = occ_val.upper()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> NormalizedTransportEvent:
        data_copy = dict(data)
        # Ensure event_id is generated if not provided
        if "event_id" not in data_copy or not data_copy["event_id"]:
            data_copy["event_id"] = str(uuid.uuid4())
        return cls(**data_copy)

    @classmethod
    def from_json(cls, json_str: str) -> NormalizedTransportEvent:
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise SchemaValidationError(f"Invalid JSON string: {e}")
        return cls.from_dict(data)

    @classmethod
    def create_sample(
        cls,
        vehicle_id: str = "BUS-101",
        mode: str = "bus",
        route_id: str = "ROUTE-12",
        latitude: float = 12.9716,
        longitude: float = 80.2440,
        speed: float = 42.0,
        heading: float = 180.0,
        status: str = "MOVING",
    ) -> NormalizedTransportEvent:
        now_utc = datetime.now(timezone.utc).isoformat()
        return cls(
            vehicle_id=vehicle_id,
            mode=mode,
            route_id=route_id,
            latitude=latitude,
            longitude=longitude,
            speed=speed,
            heading=heading,
            status=status,
            timestamp=now_utc,
        )
