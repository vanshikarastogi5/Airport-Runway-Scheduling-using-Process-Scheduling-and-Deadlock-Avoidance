"""
Main airport management system that coordinates all components.
Handles runway scheduling, deadlock prevention, and aircraft management.
"""

import threading
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import random
import json

from aircraft import Aircraft, AircraftType, AircraftStatus
from runway import Runway, RunwayStatus
from scheduler import Scheduler, SchedulingAlgorithm
from deadlock_detector import DeadlockDetector

class AirportManager:
    """Main airport management system."""
    
    def __init__(self, num_runways: int = 3, algorithm: SchedulingAlgorithm = SchedulingAlgorithm.PRIORITY):
        self.runways = []
        self.scheduler = Scheduler(algorithm)
        self.deadlock_detector = DeadlockDetector()
        self.aircraft_registry = {}
        self.running = False
        self.simulation_time = 0
        self.lock = threading.Lock()
        self.stats = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'average_wait_time': 0,
            'deadlock_events': 0
        }
        
        # Initialize runways
        self._initialize_runways(num_runways)
        
        # Start deadlock detection
        self.deadlock_detector.start_detection()
        self.deadlock_detector.add_deadlock_callback(self._handle_deadlock)
    
    def _initialize_runways(self, num_runways: int):
        """Initialize runways."""
        for i in range(num_runways):
            runway = Runway(f"RWY_{i+1:02d}")
            self.runways.append(runway)
            self.deadlock_detector.register_resource(runway.id)
    
    def add_aircraft(self, aircraft_type: AircraftType, operation_type: str = "landing", 
                   emergency: bool = False, fuel_level: float = 100.0) -> str:
        """Add a new aircraft to the system."""
        aircraft_id = f"AC_{len(self.aircraft_registry) + 1:04d}"
        aircraft = Aircraft(aircraft_id, aircraft_type, fuel_level, emergency)
        
        with self.lock:
            self.aircraft_registry[aircraft_id] = aircraft
            self.scheduler.add_aircraft(aircraft, operation_type)
            self.deadlock_detector.register_process(aircraft_id)
        
        return aircraft_id
    
    def process_operations(self):
        """Process aircraft operations on available runways."""
        with self.lock:
            for runway in self.runways:
                if runway.is_available():
                    # Try to get next aircraft for landing
                    aircraft = self.scheduler.get_next_aircraft("landing")
                    if aircraft:
                        if self._allocate_runway(runway, aircraft, "landing"):
                            self.stats['successful_operations'] += 1
                            continue
                    
                    # Try to get next aircraft for takeoff
                    aircraft = self.scheduler.get_next_aircraft("takeoff")
                    if aircraft:
                        if self._allocate_runway(runway, aircraft, "takeoff"):
                            self.stats['successful_operations'] += 1
                            continue
                
                # Check if current operation is complete
                elif runway.is_operation_complete():
                    aircraft = runway.release()
                    if aircraft:
                        self._complete_operation(aircraft)
    
    def _allocate_runway(self, runway: Runway, aircraft: Aircraft, operation_type: str) -> bool:
        """Allocate runway to aircraft."""
        # Check deadlock prevention
        if not self.deadlock_detector.prevention.can_allocate(aircraft.id, runway.id, {}):
            return False
        
        # Register resource request
        self.deadlock_detector.request_resource(aircraft.id, runway.id)
        
        # Allocate runway
        if runway.allocate(aircraft, operation_type):
            self.deadlock_detector.allocate_resource(aircraft.id, runway.id)
            aircraft.status = AircraftStatus.LANDING if operation_type == "landing" else AircraftStatus.TAKEOFF
            return True
        
        return False
    
    def _complete_operation(self, aircraft: Aircraft):
        """Complete aircraft operation."""
        runway_id = None
        for runway in self.runways:
            if runway.current_aircraft == aircraft:
                runway_id = runway.id
                break
        
        if runway_id:
            self.deadlock_detector.release_resource(aircraft.id, runway_id)
        
        # Update aircraft status
        if aircraft.status == AircraftStatus.LANDING:
            aircraft.status = AircraftStatus.LANDED
            aircraft.landing_time = datetime.now()
        elif aircraft.status == AircraftStatus.TAKEOFF:
            aircraft.status = AircraftStatus.DEPARTED
            aircraft.takeoff_time = datetime.now()
        
        self.stats['total_operations'] += 1
    
    def _handle_deadlock(self, deadlock_info: Dict):
        """Handle detected deadlock."""
        self.stats['deadlock_events'] += 1
        print(f"DEADLOCK DETECTED: {deadlock_info}")
        
        # Resolve deadlock
        processes_to_terminate = self.deadlock_detector.resolve_deadlock(deadlock_info)
        for process_id in processes_to_terminate:
            self._handle_emergency_landing(process_id)
    
    def _handle_emergency_landing(self, aircraft_id: str):
        """Handle emergency landing for deadlock resolution."""
        if aircraft_id in self.aircraft_registry:
            aircraft = self.aircraft_registry[aircraft_id]
            aircraft.emergency = True
            aircraft.priority = 0  # Highest priority
            print(f"EMERGENCY LANDING: {aircraft_id}")
    
    def update_system(self):
        """Update system state."""
        with self.lock:
            # Update waiting times
            self.scheduler.update_waiting_times()
            
            # Process operations
            self.process_operations()
            
            # Update simulation time
            self.simulation_time += 1
    
    def get_system_status(self) -> Dict:
        """Get current system status."""
        with self.lock:
            runway_status = []
            for runway in self.runways:
                runway_status.append({
                    'id': runway.id,
                    'status': runway.status.value,
                    'current_aircraft': runway.current_aircraft.id if runway.current_aircraft else None,
                    'remaining_time': runway.get_remaining_time()
                })
            
            queue_status = self.scheduler.get_queue_status()
            deadlock_status = self.deadlock_detector.get_deadlock_status()
            
            return {
                'simulation_time': self.simulation_time,
                'runways': runway_status,
                'queues': queue_status,
                'deadlock_status': deadlock_status,
                'statistics': self.stats.copy()
            }
    
    def get_detailed_status(self) -> Dict:
        """Get detailed system status."""
        with self.lock:
            status = self.get_system_status()
            status['queue_details'] = self.scheduler.get_queue_details()
            status['scheduling_history'] = self.scheduler.get_scheduling_history()[-10:]  # Last 10 events
            return status
    
    def change_scheduling_algorithm(self, algorithm: SchedulingAlgorithm):
        """Change scheduling algorithm."""
        with self.lock:
            self.scheduler.set_algorithm(algorithm)
            print(f"Scheduling algorithm changed to: {algorithm.value}")
    
    def get_statistics(self) -> Dict:
        """Get comprehensive statistics."""
        with self.lock:
            stats = self.stats.copy()
            stats.update(self.scheduler.get_statistics())
            stats['deadlock_status'] = self.deadlock_detector.get_deadlock_status()
            return stats
    
    def generate_report(self) -> str:
        """Generate a comprehensive report."""
        status = self.get_detailed_status()
        stats = self.get_statistics()
        
        report = f"""
AIRPORT MANAGEMENT SYSTEM REPORT
================================
Simulation Time: {status['simulation_time']}
Current Algorithm: {status['queues']['algorithm']}

RUNWAY STATUS:
"""
        for runway in status['runways']:
            report += f"  {runway['id']}: {runway['status']}"
            if runway['current_aircraft']:
                report += f" - Aircraft: {runway['current_aircraft']} (Remaining: {runway['remaining_time']:.1f}s)"
            report += "\n"
        
        report += f"""
QUEUE STATUS:
  Landing Queue: {status['queues']['landing_queue_size']} aircraft
  Takeoff Queue: {status['queues']['takeoff_queue_size']} aircraft
  Emergency Queue: {status['queues']['emergency_queue_size']} aircraft

STATISTICS:
  Total Operations: {stats['total_operations']}
  Successful Operations: {stats['successful_operations']}
  Failed Operations: {stats['failed_operations']}
  Deadlock Events: {stats['deadlock_events']}

DEADLOCK STATUS:
  Has Deadlock: {status['deadlock_status']['has_deadlock']}
  Processes in Deadlock: {len(status['deadlock_status']['processes_in_deadlock'])}
"""
        return report
    
    def start_simulation(self):
        """Start the simulation."""
        self.running = True
        print("Airport simulation started...")
    
    def stop_simulation(self):
        """Stop the simulation."""
        self.running = False
        self.deadlock_detector.stop_detection()
        print("Airport simulation stopped.")
    
    def run_simulation_step(self):
        """Run one simulation step."""
        if self.running:
            self.update_system()
    
    def simulate_random_aircraft(self):
        """Simulate random aircraft arrivals."""
        aircraft_types = list(AircraftType)
        operation_types = ["landing", "takeoff"]
        
        # Random aircraft arrival
        if random.random() < 0.3:  # 30% chance per step
            aircraft_type = random.choice(aircraft_types)
            operation_type = random.choice(operation_types)
            emergency = random.random() < 0.05  # 5% emergency
            fuel_level = random.uniform(10, 100)
            
            aircraft_id = self.add_aircraft(aircraft_type, operation_type, emergency, fuel_level)
            print(f"New aircraft arrived: {aircraft_id} ({aircraft_type.name}) - {operation_type}")
    
    def cleanup(self):
        """Cleanup resources."""
        self.stop_simulation()
        with self.lock:
            self.aircraft_registry.clear()
            self.scheduler.clear_history()