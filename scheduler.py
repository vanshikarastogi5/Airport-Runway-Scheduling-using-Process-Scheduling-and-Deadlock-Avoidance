"""
Scheduling algorithms for airport runway management.
Implements FCFS, Priority, Round Robin, and Multilevel Queue scheduling.
"""

from enum import Enum
from typing import List, Optional, Dict
import heapq
from collections import deque
from datetime import datetime
import threading

class SchedulingAlgorithm(Enum):
    """Available scheduling algorithms."""
    FCFS = "first_come_first_served"
    PRIORITY = "priority"
    ROUND_ROBIN = "round_robin"
    MULTILEVEL_QUEUE = "multilevel_queue"

class Scheduler:
    """Main scheduler for airport runway management."""

    def __init__(self, algorithm: SchedulingAlgorithm = SchedulingAlgorithm.PRIORITY):
        self.algorithm = algorithm
        self.landing_queue = []
        self.takeoff_queue = []
        self.emergency_queue = []
        self.lock = threading.Lock()
        self.time_quantum = 300  # 5 minutes for Round Robin
        self.current_time = 0
        self.scheduling_history = []
        self._initialize_queues()

    def _initialize_queues(self):
        """Initialize queues based on algorithm."""
        if self.algorithm == SchedulingAlgorithm.ROUND_ROBIN:
            self.landing_queue = deque()
            self.takeoff_queue = deque()
            self.emergency_queue = deque()
        else:
            self.landing_queue = []
            self.takeoff_queue = []
            self.emergency_queue = []

    def add_aircraft(self, aircraft, operation_type: str = "landing"):
        """Add aircraft to appropriate queue."""
        with self.lock:
            if aircraft.is_emergency():
                self._add_to_emergency_queue(aircraft)
            elif operation_type == "landing":
                self._add_to_landing_queue(aircraft)
            elif operation_type == "takeoff":
                self._add_to_takeoff_queue(aircraft)

            self._log_scheduling_event("aircraft_added", aircraft, operation_type)

    def _add_to_landing_queue(self, aircraft):
        if self.algorithm == SchedulingAlgorithm.FCFS:
            self.landing_queue.append(aircraft)
        elif self.algorithm == SchedulingAlgorithm.PRIORITY:
            heapq.heappush(self.landing_queue, aircraft)
        elif self.algorithm == SchedulingAlgorithm.ROUND_ROBIN:
            self.landing_queue.append(aircraft)
        elif self.algorithm == SchedulingAlgorithm.MULTILEVEL_QUEUE:
            if aircraft.priority <= 1:
                heapq.heappush(self.landing_queue, aircraft)
            else:
                self.landing_queue.append(aircraft)

    def _add_to_takeoff_queue(self, aircraft):
        if self.algorithm == SchedulingAlgorithm.FCFS:
            self.takeoff_queue.append(aircraft)
        elif self.algorithm == SchedulingAlgorithm.PRIORITY:
            heapq.heappush(self.takeoff_queue, aircraft)
        elif self.algorithm == SchedulingAlgorithm.ROUND_ROBIN:
            self.takeoff_queue.append(aircraft)
        elif self.algorithm == SchedulingAlgorithm.MULTILEVEL_QUEUE:
            if aircraft.priority <= 1:
                heapq.heappush(self.takeoff_queue, aircraft)
            else:
                self.takeoff_queue.append(aircraft)

    def _add_to_emergency_queue(self, aircraft):
        if self.algorithm == SchedulingAlgorithm.ROUND_ROBIN:
            self.emergency_queue.append(aircraft)
        else:
            heapq.heappush(self.emergency_queue, aircraft)

    def get_next_aircraft(self, operation_type: str = "landing") -> Optional[object]:
        """Get next aircraft to schedule."""
        with self.lock:
            if self.emergency_queue:
                return self._get_from_emergency_queue()

            if operation_type == "landing" and self.landing_queue:
                return self._get_from_landing_queue()
            elif operation_type == "takeoff" and self.takeoff_queue:
                return self._get_from_takeoff_queue()

            return None

    def _get_from_emergency_queue(self):
        if self.algorithm == SchedulingAlgorithm.ROUND_ROBIN:
            return self.emergency_queue.popleft() if self.emergency_queue else None
        else:
            return heapq.heappop(self.emergency_queue) if self.emergency_queue else None

    def _get_from_landing_queue(self):
        if self.algorithm == SchedulingAlgorithm.FCFS:
            return self.landing_queue.pop(0) if self.landing_queue else None
        elif self.algorithm == SchedulingAlgorithm.PRIORITY:
            return heapq.heappop(self.landing_queue) if self.landing_queue else None
        elif self.algorithm == SchedulingAlgorithm.ROUND_ROBIN:
            return self.landing_queue.popleft() if self.landing_queue else None
        elif self.algorithm == SchedulingAlgorithm.MULTILEVEL_QUEUE:
            if self.landing_queue and hasattr(self.landing_queue[0], 'priority') and self.landing_queue[0].priority <= 1:
                return heapq.heappop(self.landing_queue)
            else:
                return self.landing_queue.pop(0) if self.landing_queue else None

    def _get_from_takeoff_queue(self):
        if self.algorithm == SchedulingAlgorithm.FCFS:
            return self.takeoff_queue.pop(0) if self.takeoff_queue else None
        elif self.algorithm == SchedulingAlgorithm.PRIORITY:
            return heapq.heappop(self.takeoff_queue) if self.takeoff_queue else None
        elif self.algorithm == SchedulingAlgorithm.ROUND_ROBIN:
            return self.takeoff_queue.popleft() if self.takeoff_queue else None
        elif self.algorithm == SchedulingAlgorithm.MULTILEVEL_QUEUE:
            if self.takeoff_queue and hasattr(self.takeoff_queue[0], 'priority') and self.takeoff_queue[0].priority <= 1:
                return heapq.heappop(self.takeoff_queue)
            else:
                return self.takeoff_queue.pop(0) if self.takeoff_queue else None

    def update_waiting_times(self):
        with self.lock:
            for aircraft in self.landing_queue + self.takeoff_queue + list(self.emergency_queue):
                aircraft.update_waiting_time()

    def get_queue_status(self) -> Dict:
        with self.lock:
            return {
                'landing_queue_size': len(self.landing_queue),
                'takeoff_queue_size': len(self.takeoff_queue),
                'emergency_queue_size': len(self.emergency_queue),
                'algorithm': self.algorithm.value,
                'total_waiting': len(self.landing_queue) + len(self.takeoff_queue) + len(self.emergency_queue)
            }

    def _log_scheduling_event(self, event_type: str, aircraft, operation_type: str = None):
        event = {
            'timestamp': datetime.now(),
            'event_type': event_type,
            'aircraft_id': aircraft.id,
            'aircraft_type': aircraft.type.name,
            'priority': aircraft.priority,
            'operation_type': operation_type,
            'algorithm': self.algorithm.value
        }
        self.scheduling_history.append(event)

    def get_scheduling_history(self) -> List[Dict]:
        return self.scheduling_history.copy()

    def clear_history(self):
        self.scheduling_history.clear()

    def set_algorithm(self, algorithm: SchedulingAlgorithm):
        """Change scheduling algorithm and preserve queues."""
        with self.lock:
            old_landing = list(self.landing_queue)
            old_takeoff = list(self.takeoff_queue)
            old_emergency = list(self.emergency_queue)

            self.algorithm = algorithm
            self._initialize_queues()

            for aircraft in old_landing:
                self._add_to_landing_queue(aircraft)
            for aircraft in old_takeoff:
                self._add_to_takeoff_queue(aircraft)
            for aircraft in old_emergency:
                self._add_to_emergency_queue(aircraft)

    def get_statistics(self) -> Dict:
        if not self.scheduling_history:
            return {}
        total_ops = len(self.scheduling_history)
        aircraft_types = {}
        priority_dist = {}
        for event in self.scheduling_history:
            aircraft_types[event['aircraft_type']] = aircraft_types.get(event['aircraft_type'], 0) + 1
            priority_dist[event['priority']] = priority_dist.get(event['priority'], 0) + 1
        return {
            'total_operations': total_ops,
            'aircraft_type_distribution': aircraft_types,
            'priority_distribution': priority_dist,
            'current_algorithm': self.algorithm.value
        }
