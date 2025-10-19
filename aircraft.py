from enum import Enum
from datetime import datetime

class AircraftType(Enum):
    EMERGENCY = 1
    MILITARY = 2
    COMMERCIAL = 3
    PRIVATE = 4
    CARGO = 5
    TRAINING = 6

class AircraftStatus(Enum):
    WAITING = "waiting"
    APPROACHING = "approaching"
    LANDING = "landing"
    TAKEOFF = "takeoff"
    DEPARTED = "departed"
    LANDED = "landed"

class Aircraft:
    def __init__(self, aircraft_id: str, aircraft_type: AircraftType, 
                 fuel_level: float = 100.0, emergency: bool = False,
                 scheduled_time: datetime = None):
        self.id = aircraft_id
        self.type = aircraft_type
        self.fuel_level = fuel_level
        self.emergency = emergency
        self.status = AircraftStatus.WAITING
        self.scheduled_time = scheduled_time or datetime.now()
        self.priority = self._calculate_priority()
        self.waiting_time = 0
        self.landing_time = None
        self.takeoff_time = None
        
    def _calculate_priority(self) -> int:
        base_priority = self.type.value
        if self.emergency:
            return 0
        if self.fuel_level < 20:
            return base_priority - 1
        return base_priority
    
    def update_waiting_time(self, time_increment: int = 1):
        self.waiting_time += time_increment
        if self.waiting_time > 30:
            self.priority = max(0, self.priority - 1)
    
    def is_emergency(self) -> bool:
        return self.emergency or self.fuel_level < 10
    
    def __lt__(self, other):
        if self.priority != other.priority:
            return self.priority < other.priority
        return self.scheduled_time < other.scheduled_time
    
    def __str__(self):
        return f"Aircraft {self.id} ({self.type.name}) - Priority: {self.priority}, Status: {self.status.value}"
    
    def __repr__(self):
        return f"Aircraft(id='{self.id}', type={self.type}, priority={self.priority})"
