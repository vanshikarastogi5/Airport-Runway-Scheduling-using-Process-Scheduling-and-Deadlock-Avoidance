"""
Simulation framework for airport runway scheduling system.
Provides testing, benchmarking, and analysis capabilities.
"""

import time
import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import threading
# import matplotlib.pyplot as plt
# import numpy as np

from airport_manager import AirportManager
from aircraft import AircraftType
from scheduler import SchedulingAlgorithm

class Simulation:
    """Main simulation class for airport management system."""
    
    def __init__(self, num_runways: int = 3, algorithm: SchedulingAlgorithm = SchedulingAlgorithm.PRIORITY):
        self.airport = AirportManager(num_runways, algorithm)
        self.simulation_data = []
        self.running = False
        self.step_count = 0
        self.max_steps = 1000
        
    def run_basic_simulation(self, duration: int = 100):
        """Run a basic simulation with random aircraft arrivals."""
        print("Starting basic simulation...")
        self.airport.start_simulation()
        
        for step in range(duration):
            # Simulate random aircraft arrivals
            self.airport.simulate_random_aircraft()
            
            # Run simulation step
            self.airport.run_simulation_step()
            
            # Log status every 10 steps
            if step % 10 == 0:
                status = self.airport.get_system_status()
                self.simulation_data.append({
                    'step': step,
                    'timestamp': datetime.now(),
                    'status': status
                })
                print(f"Step {step}: Queues - Landing: {status['queues']['landing_queue_size']}, "
                      f"Takeoff: {status['queues']['takeoff_queue_size']}, "
                      f"Emergency: {status['queues']['emergency_queue_size']}")
        
        self.airport.stop_simulation()
        print("Basic simulation completed.")
        return self.simulation_data
    
    def run_algorithm_comparison(self, duration: int = 200) -> Dict:
        """Compare different scheduling algorithms."""
        algorithms = [
            SchedulingAlgorithm.FCFS,
            SchedulingAlgorithm.PRIORITY,
            SchedulingAlgorithm.ROUND_ROBIN,
            SchedulingAlgorithm.MULTILEVEL_QUEUE
        ]
        
        results = {}
        
        for algorithm in algorithms:
            print(f"\nTesting {algorithm.value}...")
            
            # Create new airport manager for each algorithm
            airport = AirportManager(3, algorithm)
            airport.start_simulation()
            
            algorithm_data = []
            
            for step in range(duration):
                # Simulate aircraft arrivals
                if random.random() < 0.4:  # 40% chance
                    aircraft_type = random.choice(list(AircraftType))
                    operation_type = random.choice(["landing", "takeoff"])
                    emergency = random.random() < 0.1  # 10% emergency
                    fuel_level = random.uniform(15, 100)
                    
                    airport.add_aircraft(aircraft_type, operation_type, emergency, fuel_level)
                
                airport.run_simulation_step()
                
                # Record data every 5 steps
                if step % 5 == 0:
                    status = airport.get_system_status()
                    algorithm_data.append({
                        'step': step,
                        'total_waiting': status['queues']['total_waiting'],
                        'successful_operations': status['statistics']['successful_operations'],
                        'deadlock_events': status['statistics']['deadlock_events']
                    })
            
            airport.stop_simulation()
            results[algorithm.value] = algorithm_data
        
        return results
    
    def run_stress_test(self, num_aircraft: int = 100) -> Dict:
        """Run stress test with high aircraft load."""
        print(f"Running stress test with {num_aircraft} aircraft...")
        
        self.airport.start_simulation()
        
        # Add many aircraft quickly
        for i in range(num_aircraft):
            aircraft_type = random.choice(list(AircraftType))
            operation_type = random.choice(["landing", "takeoff"])
            emergency = random.random() < 0.05  # 5% emergency
            fuel_level = random.uniform(5, 100)
            
            self.airport.add_aircraft(aircraft_type, operation_type, emergency, fuel_level)
        
        # Run simulation until all aircraft are processed
        max_steps = 2000
        step = 0
        
        while step < max_steps:
            self.airport.run_simulation_step()
            step += 1
            
            # Check if all aircraft are processed
            status = self.airport.get_system_status()
            if (status['queues']['total_waiting'] == 0 and 
                all(runway['status'] == 'available' for runway in status['runways'])):
                break
        
        self.airport.stop_simulation()
        
        final_stats = self.airport.get_statistics()
        return {
            'aircraft_processed': final_stats['successful_operations'],
            'total_steps': step,
            'deadlock_events': final_stats['deadlock_events'],
            'final_statistics': final_stats
        }
    
    def run_deadlock_test(self) -> Dict:
        """Test deadlock detection and resolution."""
        print("Running deadlock test...")
        
        # Create scenario that might cause deadlock
        self.airport.start_simulation()
        
        # Add aircraft with low fuel (high priority)
        for i in range(5):
            self.airport.add_aircraft(AircraftType.COMMERCIAL, "landing", True, 5.0)
        
        # Add normal aircraft
        for i in range(10):
            self.airport.add_aircraft(AircraftType.COMMERCIAL, "landing", False, 50.0)
        
        # Run simulation
        deadlock_events = 0
        for step in range(100):
            self.airport.run_simulation_step()
            
            status = self.airport.get_system_status()
            if status['deadlock_status']['has_deadlock']:
                deadlock_events += 1
                print(f"Deadlock detected at step {step}")
        
        self.airport.stop_simulation()
        
        return {
            'deadlock_events': deadlock_events,
            'final_status': self.airport.get_system_status()
        }
    
    def generate_performance_report(self, results: Dict) -> str:
        """Generate performance report from simulation results."""
        report = "AIRPORT SCHEDULING PERFORMANCE REPORT\n"
        report += "=" * 50 + "\n\n"
        
        for algorithm, data in results.items():
            if not data:
                continue
                
            report += f"Algorithm: {algorithm}\n"
            report += "-" * 30 + "\n"
            
            # Calculate metrics
            total_waiting = [d['total_waiting'] for d in data]
            successful_ops = [d['successful_operations'] for d in data]
            deadlock_events = [d['deadlock_events'] for d in data]
            
            report += f"Average Queue Size: {sum(total_waiting)/len(total_waiting):.2f}\n"
            report += f"Max Queue Size: {max(total_waiting)}\n"
            report += f"Final Successful Operations: {successful_ops[-1] if successful_ops else 0}\n"
            report += f"Total Deadlock Events: {deadlock_events[-1] if deadlock_events else 0}\n"
            report += "\n"
        
        return report
    
    def plot_simulation_results(self, results: Dict, save_path: str = "simulation_results.png"):
        """Plot simulation results."""
        print("Plotting functionality disabled - matplotlib not available")
        print("Results data available for manual analysis:")
        for algorithm, data in results.items():
            if data:
                print(f"{algorithm}: {len(data)} data points")
    
    def run_comprehensive_test(self):
        """Run comprehensive test suite."""
        print("Running comprehensive test suite...")
        
        # Test 1: Basic simulation
        print("\n1. Basic Simulation Test")
        basic_results = self.run_basic_simulation(50)
        
        # Test 2: Algorithm comparison
        print("\n2. Algorithm Comparison Test")
        comparison_results = self.run_algorithm_comparison(100)
        
        # Test 3: Stress test
        print("\n3. Stress Test")
        stress_results = self.run_stress_test(50)
        
        # Test 4: Deadlock test
        print("\n4. Deadlock Test")
        deadlock_results = self.run_deadlock_test()
        
        # Generate reports
        print("\n5. Generating Reports...")
        performance_report = self.generate_performance_report(comparison_results)
        
        # Save results
        with open('simulation_results.json', 'w') as f:
            json.dump({
                'basic_results': basic_results,
                'comparison_results': comparison_results,
                'stress_results': stress_results,
                'deadlock_results': deadlock_results
            }, f, indent=2, default=str)
        
        with open('performance_report.txt', 'w') as f:
            f.write(performance_report)
        
        # Plot results
        self.plot_simulation_results(comparison_results)
        
        print("\nComprehensive test completed!")
        print("Results saved to simulation_results.json")
        print("Performance report saved to performance_report.txt")
        print("Plots saved to simulation_results.png")
        
        return {
            'basic_results': basic_results,
            'comparison_results': comparison_results,
            'stress_results': stress_results,
            'deadlock_results': deadlock_results,
            'performance_report': performance_report
        }