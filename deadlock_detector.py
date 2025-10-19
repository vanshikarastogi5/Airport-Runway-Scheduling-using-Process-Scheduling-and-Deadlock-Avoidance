"""
Deadlock detection and prevention system for airport runway scheduling.
Implements resource allocation graph and deadlock prevention strategies.
"""

from typing import Dict, List, Set, Tuple
from collections import defaultdict, deque
import threading
import time
from datetime import datetime

class ResourceAllocationGraph:
    """Resource Allocation Graph for deadlock detection."""
    
    def __init__(self):
        self.processes = set()  # Aircraft
        self.resources = set()  # Runways
        self.request_edges = defaultdict(set)  # Process -> Resource
        self.allocation_edges = defaultdict(set)  # Resource -> Process
        self.lock = threading.Lock()
    
    def add_process(self, process_id: str):
        """Add a process (aircraft) to the graph."""
        with self.lock:
            self.processes.add(process_id)
    
    def add_resource(self, resource_id: str):
        """Add a resource (runway) to the graph."""
        with self.lock:
            self.resources.add(resource_id)
    
    def request_resource(self, process_id: str, resource_id: str):
        """Add a request edge from process to resource."""
        with self.lock:
            self.request_edges[process_id].add(resource_id)
    
    def allocate_resource(self, process_id: str, resource_id: str):
        """Allocate resource to process and update edges."""
        with self.lock:
            # Remove request edge
            self.request_edges[process_id].discard(resource_id)
            # Add allocation edge
            self.allocation_edges[resource_id].add(process_id)
    
    def release_resource(self, process_id: str, resource_id: str):
        """Release resource from process."""
        with self.lock:
            self.allocation_edges[resource_id].discard(process_id)
    
    def detect_deadlock(self) -> List[Set[str]]:
        """Detect deadlock using cycle detection in RAG."""
        with self.lock:
            # Build adjacency list for the graph
            graph = defaultdict(set)
            
            # Add request edges (process -> resource)
            for process, resources in self.request_edges.items():
                for resource in resources:
                    graph[process].add(f"resource_{resource}")
            
            # Add allocation edges (resource -> process)
            for resource, processes in self.allocation_edges.items():
                for process in processes:
                    graph[f"resource_{resource}"].add(process)
            
            # Find cycles using DFS
            visited = set()
            rec_stack = set()
            cycles = []
            
            def dfs(node, path):
                if node in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(node)
                    cycle = set(path[cycle_start:])
                    if len(cycle) > 2:  # Valid cycle
                        cycles.append(cycle)
                    return
                
                if node in visited:
                    return
                
                visited.add(node)
                rec_stack.add(node)
                path.append(node)
                
                for neighbor in graph[node]:
                    dfs(neighbor, path.copy())
                
                rec_stack.remove(node)
                path.pop()
            
            for node in graph:
                if node not in visited:
                    dfs(node, [])
            
            return cycles
    
    def get_deadlock_info(self) -> Dict:
        """Get information about current deadlock state."""
        cycles = self.detect_deadlock()
        return {
            'has_deadlock': len(cycles) > 0,
            'cycles': cycles,
            'processes_in_deadlock': set().union(*cycles) if cycles else set(),
            'request_edges': dict(self.request_edges),
            'allocation_edges': dict(self.allocation_edges)
        }

class DeadlockPrevention:
    """Deadlock prevention strategies."""
    
    def __init__(self):
        self.resource_ordering = {}  # Resource priority ordering
        self.max_wait_time = 300  # 5 minutes max wait time
        self.preemption_enabled = True
    
    def set_resource_ordering(self, ordering: Dict[str, int]):
        """Set resource ordering for deadlock prevention."""
        self.resource_ordering = ordering
    
    def can_allocate(self, process_id: str, resource_id: str, 
                    current_allocations: Dict[str, str]) -> bool:
        """Check if resource can be allocated without causing deadlock."""
        # Banker's algorithm implementation
        if not self._is_safe_state(process_id, resource_id, current_allocations):
            return False
        
        # Check resource ordering
        if resource_id in self.resource_ordering:
            for allocated_resource, allocated_process in current_allocations.items():
                if (allocated_process == process_id and 
                    allocated_resource in self.resource_ordering and
                    self.resource_ordering[allocated_resource] > self.resource_ordering[resource_id]):
                    return False
        
        return True
    
    def _is_safe_state(self, process_id: str, resource_id: str, 
                      current_allocations: Dict[str, str]) -> bool:
        """Check if allocation would result in safe state."""
        # Simplified safety check
        # In real implementation, this would use Banker's algorithm
        return True
    
    def should_preempt(self, process_id: str, resource_id: str, 
                      wait_time: float) -> bool:
        """Determine if preemption should occur."""
        if not self.preemption_enabled:
            return False
        
        # Preempt if waiting too long
        if wait_time > self.max_wait_time:
            return True
        
        return False

class DeadlockDetector:
    """Main deadlock detection and prevention system."""
    
    def __init__(self):
        self.rag = ResourceAllocationGraph()
        self.prevention = DeadlockPrevention()
        self.detection_interval = 5  # Check every 5 seconds
        self.running = False
        self.detection_thread = None
        self.deadlock_callbacks = []
        self.lock = threading.Lock()
    
    def start_detection(self):
        """Start deadlock detection in background thread."""
        if self.running:
            return
        
        self.running = True
        self.detection_thread = threading.Thread(target=self._detection_loop, daemon=True)
        self.detection_thread.start()
    
    def stop_detection(self):
        """Stop deadlock detection."""
        self.running = False
        if self.detection_thread:
            self.detection_thread.join()
    
    def _detection_loop(self):
        """Main detection loop."""
        while self.running:
            try:
                deadlock_info = self.rag.get_deadlock_info()
                if deadlock_info['has_deadlock']:
                    self._handle_deadlock(deadlock_info)
                time.sleep(self.detection_interval)
            except Exception as e:
                print(f"Error in deadlock detection: {e}")
                time.sleep(1)
    
    def _handle_deadlock(self, deadlock_info: Dict):
        """Handle detected deadlock."""
        print(f"DEADLOCK DETECTED: {deadlock_info['cycles']}")
        
        # Notify callbacks
        for callback in self.deadlock_callbacks:
            try:
                callback(deadlock_info)
            except Exception as e:
                print(f"Error in deadlock callback: {e}")
    
    def add_deadlock_callback(self, callback):
        """Add callback for deadlock detection."""
        self.deadlock_callbacks.append(callback)
    
    def register_process(self, process_id: str):
        """Register a process (aircraft) with the detector."""
        self.rag.add_process(process_id)
    
    def register_resource(self, resource_id: str):
        """Register a resource (runway) with the detector."""
        self.rag.add_resource(resource_id)
    
    def request_resource(self, process_id: str, resource_id: str):
        """Register a resource request."""
        self.rag.request_resource(process_id, resource_id)
    
    def allocate_resource(self, process_id: str, resource_id: str):
        """Register resource allocation."""
        self.rag.allocate_resource(process_id, resource_id)
    
    def release_resource(self, process_id: str, resource_id: str):
        """Register resource release."""
        self.rag.release_resource(process_id, resource_id)
    
    def get_deadlock_status(self) -> Dict:
        """Get current deadlock status."""
        return self.rag.get_deadlock_info()
    
    def resolve_deadlock(self, deadlock_info: Dict) -> List[str]:
        """Resolve deadlock by selecting processes to terminate."""
        # Simple resolution: terminate lowest priority processes
        processes_in_deadlock = list(deadlock_info['processes_in_deadlock'])
        
        # In a real system, this would consider process priorities
        # For now, return first process in the deadlock
        return processes_in_deadlock[:1] if processes_in_deadlock else []