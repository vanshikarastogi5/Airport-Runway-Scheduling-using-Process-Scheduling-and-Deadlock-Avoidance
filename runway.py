"""
Runway management system for airport scheduling.
Handles runway allocation and prevents conflicts.
"""

from enum import Enum
from datetime import datetime, timedelta
from typing import Optional, List
import threading
import time

class RunwayStatus(Enum):
    """Status of runway."""
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"
    CLOSED = "closed"

class Runway:
    """Represents a runway in the airport."""
    
    def __init__(self, runway_id: str, length: float = 3000.0, 
                 width: float = 45.0, status: RunwayStatus = RunwayStatus.AVAILABLE):
        self.id = runway_id
        self.length = length
        self.width = width
        self.status = status
        self.current_aircraft = None
        self.operation_start_time = None
        self.operation_type = None  # 'landing' or 'takeoff'
        self.lock = threading.Lock()
        self.operation_duration = 0
        
    def is_available(self) -> bool:
        """Check if runway is available for operations."""
        return (self.status == RunwayStatus.AVAILABLE and 
                self.current_aircraft is None)
    
    def allocate(self, aircraft, operation_type: str) -> bool:
        """Allocate runway to aircraft for operation."""
        with self.lock:
            if not self.is_available():
                return False
            
            self.current_aircraft = aircraft
            self.operation_type = operation_type
            self.operation_start_time = datetime.now()
            self.status = RunwayStatus.OCCUPIED
            
            # Calculate operation duration based on aircraft type and operation
            self.operation_duration = self._calculate_operation_duration(aircraft, operation_type)
            return True
    
    def _calculate_operation_duration(self, aircraft, operation_type: str) -> int:
        """Calculate operation duration in seconds."""
        base_duration = 120  # 2 minutes base
        
        # Adjust based on aircraft type
        type_multipliers = {
            'EMERGENCY': 0.8,
            'MILITARY': 1.2,
            'COMMERCIAL': 1.0,
            'PRIVATE': 0.9,
            'CARGO': 1.3,
            'TRAINING': 1.1
        }
        
        multiplier = type_multipliers.get(aircraft.type.name, 1.0)
        
        # Emergency operations are faster
        if aircraft.is_emergency():
            multiplier *= 0.7
            
        return int(base_duration * multiplier)
    
    def is_operation_complete(self) -> bool:
        """Check if current operation is complete."""
        if not self.current_aircraft or not self.operation_start_time:
            return True
            
        elapsed = (datetime.now() - self.operation_start_time).total_seconds()
        return elapsed >= self.operation_duration
    
    def release(self) -> Optional[object]:
        """Release runway and return the aircraft."""
        with self.lock:
            if not self.current_aircraft:
                return None
                
            aircraft = self.current_aircraft
            self.current_aircraft = None
            self.operation_type = None
            self.operation_start_time = None
            self.status = RunwayStatus.AVAILABLE
            self.operation_duration = 0
            
            return aircraft
    
    def get_remaining_time(self) -> float:
        """Get remaining time for current operation."""
        if not self.current_aircraft or not self.operation_start_time:
            return 0
            
        elapsed = (datetime.now() - self.operation_start_time).total_seconds()
        return max(0, self.operation_duration - elapsed)
    
    def __str__(self):
        status_info = f"Status: {self.status.value}"
        if self.current_aircraft:
            status_info += f", Aircraft: {self.current_aircraft.id}"
            status_info += f", Remaining: {self.get_remaining_time():.1f}s"
        return f"Runway {self.id} - {status_info}"
    
    def __repr__(self):
        return f"Runway(id='{self.id}', status={self.status}, aircraft={self.current_aircraft})"