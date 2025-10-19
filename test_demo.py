"""
Simple demonstration script for the Airport Runway Scheduling System.
Shows basic functionality and system capabilities.
"""

from airport_manager import AirportManager
from aircraft import AircraftType
from scheduler import SchedulingAlgorithm
import time

def run_basic_demo():
    """Run a basic demonstration of the system."""
    print("="*60)
    print("AIRPORT RUNWAY SCHEDULING SYSTEM - BASIC DEMO")
    print("="*60)
    
    # Initialize airport with 3 runways and priority scheduling
    print("\n1. Initializing Airport System...")
    airport = AirportManager(3, SchedulingAlgorithm.PRIORITY)
    print("   ✓ Airport initialized with 3 runways")
    print("   ✓ Priority scheduling algorithm enabled")
    print("   ✓ Deadlock detection system active")
    
    # Add various aircraft
    print("\n2. Adding Aircraft to System...")
    
    # Emergency aircraft (highest priority)
    emergency_id = airport.add_aircraft(AircraftType.EMERGENCY, "landing", True, 5.0)
    print(f"   ✓ Added emergency aircraft: {emergency_id} (Priority: 0)")
    
    # Military aircraft
    military_id = airport.add_aircraft(AircraftType.MILITARY, "takeoff", False, 80.0)
    print(f"   ✓ Added military aircraft: {military_id} (Priority: 2)")
    
    # Commercial aircraft
    commercial_ids = []
    for i in range(3):
        aircraft_id = airport.add_aircraft(AircraftType.COMMERCIAL, "landing", False, 50.0)
        commercial_ids.append(aircraft_id)
    print(f"   ✓ Added 3 commercial aircraft: {commercial_ids} (Priority: 3)")
    
    # Private aircraft
    private_id = airport.add_aircraft(AircraftType.PRIVATE, "landing", False, 30.0)
    print(f"   ✓ Added private aircraft: {private_id} (Priority: 4)")
    
    # Cargo aircraft
    cargo_id = airport.add_aircraft(AircraftType.CARGO, "takeoff", False, 70.0)
    print(f"   ✓ Added cargo aircraft: {cargo_id} (Priority: 5)")
    
    # Show initial status
    print("\n3. Initial System Status:")
    status = airport.get_system_status()
    print(f"   Landing Queue: {status['queues']['landing_queue_size']} aircraft")
    print(f"   Takeoff Queue: {status['queues']['takeoff_queue_size']} aircraft")
    print(f"   Emergency Queue: {status['queues']['emergency_queue_size']} aircraft")
    
    # Run simulation
    print("\n4. Running Simulation...")
    airport.start_simulation()
    
    for step in range(15):
        print(f"\n   Step {step + 1}:")
        
        # Run simulation step
        airport.run_simulation_step()
        
        # Get current status
        status = airport.get_system_status()
        
        # Show runway status
        for runway in status['runways']:
            if runway['current_aircraft']:
                print(f"     {runway['id']}: Processing {runway['current_aircraft']} "
                      f"(Remaining: {runway['remaining_time']:.1f}s)")
            else:
                print(f"     {runway['id']}: Available")
        
        # Show queue status
        print(f"     Queues - Landing: {status['queues']['landing_queue_size']}, "
              f"Takeoff: {status['queues']['takeoff_queue_size']}, "
              f"Emergency: {status['queues']['emergency_queue_size']}")
        
        # Show operations completed
        print(f"     Operations completed: {status['statistics']['successful_operations']}")
        
        # Small delay for readability
        time.sleep(0.5)
    
    airport.stop_simulation()
    
    # Show final statistics
    print("\n5. Final Statistics:")
    final_stats = airport.get_statistics()
    print(f"   Total Operations: {final_stats['total_operations']}")
    print(f"   Successful Operations: {final_stats['successful_operations']}")
    print(f"   Deadlock Events: {final_stats['deadlock_events']}")
    
    # Show final status
    final_status = airport.get_system_status()
    print(f"   Final Queue Sizes - Landing: {final_status['queues']['landing_queue_size']}, "
          f"Takeoff: {final_status['queues']['takeoff_queue_size']}")
    
    print("\n" + "="*60)
    print("DEMO COMPLETED SUCCESSFULLY!")
    print("="*60)

def run_algorithm_comparison():
    """Demonstrate different scheduling algorithms."""
    print("\n" + "="*60)
    print("ALGORITHM COMPARISON DEMO")
    print("="*60)
    
    algorithms = [
        (SchedulingAlgorithm.FCFS, "First-Come-First-Served"),
        (SchedulingAlgorithm.PRIORITY, "Priority Scheduling"),
        (SchedulingAlgorithm.ROUND_ROBIN, "Round Robin"),
        (SchedulingAlgorithm.MULTILEVEL_QUEUE, "Multi-level Queue")
    ]
    
    for algorithm, name in algorithms:
        print(f"\nTesting {name}...")
        
        # Create airport with specific algorithm
        airport = AirportManager(2, algorithm)
        
        # Add same set of aircraft
        aircraft_ids = []
        aircraft_ids.append(airport.add_aircraft(AircraftType.EMERGENCY, "landing", True, 5.0))
        aircraft_ids.append(airport.add_aircraft(AircraftType.COMMERCIAL, "landing", False, 50.0))
        aircraft_ids.append(airport.add_aircraft(AircraftType.COMMERCIAL, "landing", False, 30.0))
        aircraft_ids.append(airport.add_aircraft(AircraftType.PRIVATE, "takeoff", False, 80.0))
        aircraft_ids.append(airport.add_aircraft(AircraftType.MILITARY, "takeoff", False, 70.0))
        
        # Run simulation
        airport.start_simulation()
        for step in range(10):
            airport.run_simulation_step()
        airport.stop_simulation()
        
        # Get results
        status = airport.get_system_status()
        print(f"   Operations completed: {status['statistics']['successful_operations']}")
        print(f"   Remaining in queues: {status['queues']['total_waiting']}")

if __name__ == "__main__":
    # Run basic demo
    run_basic_demo()
    
    # Run algorithm comparison
    run_algorithm_comparison()
    
    print("\n" + "="*60)
    print("ALL DEMOS COMPLETED!")
    print("Run 'python main.py' for interactive mode.")
    print("="*60)