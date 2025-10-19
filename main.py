"""
Main application for Airport Runway Scheduling System.
Provides interactive interface and demonstration capabilities.
"""

import time
import random
import json
from datetime import datetime
from typing import Dict, List

from airport_manager import AirportManager
from aircraft import AircraftType
from scheduler import SchedulingAlgorithm
from simulation import Simulation

class AirportSchedulingApp:
    """Main application class for airport scheduling system."""
    
    def __init__(self):
        self.airport = None
        self.simulation = None
        self.running = False
    
    def initialize_system(self, num_runways: int = 3, algorithm: SchedulingAlgorithm = SchedulingAlgorithm.PRIORITY):
        """Initialize the airport management system."""
        self.airport = AirportManager(num_runways, algorithm)
        self.simulation = Simulation(num_runways, algorithm)
        print(f"Airport system initialized with {num_runways} runways using {algorithm.value} algorithm.")
    
    def interactive_demo(self):
        """Run interactive demonstration."""
        print("\n" + "="*60)
        print("AIRPORT RUNWAY SCHEDULING SYSTEM - INTERACTIVE DEMO")
        print("="*60)
        
        while True:
            print("\nOptions:")
            print("1. Initialize System")
            print("2. Add Aircraft")
            print("3. View System Status")
            print("4. Run Simulation Step")
            print("5. Change Algorithm")
            print("6. Run Auto Simulation")
            print("7. Run Comprehensive Test")
            print("8. Generate Report")
            print("9. Exit")
            
            choice = input("\nEnter your choice (1-9): ").strip()
            
            if choice == '1':
                self._initialize_system_menu()
            elif choice == '2':
                self._add_aircraft_menu()
            elif choice == '3':
                self._view_status()
            elif choice == '4':
                self._run_simulation_step()
            elif choice == '5':
                self._change_algorithm()
            elif choice == '6':
                self._run_auto_simulation()
            elif choice == '7':
                self._run_comprehensive_test()
            elif choice == '8':
                self._generate_report()
            elif choice == '9':
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please try again.")
    
    def _initialize_system_menu(self):
        """Initialize system with user input."""
        try:
            num_runways = int(input("Enter number of runways (default 3): ") or "3")
            print("\nAvailable algorithms:")
            algorithms = list(SchedulingAlgorithm)
            for i, alg in enumerate(algorithms, 1):
                print(f"{i}. {alg.value}")
            
            alg_choice = int(input("Select algorithm (1-4, default 2): ") or "2")
            algorithm = algorithms[alg_choice - 1]
            
            self.initialize_system(num_runways, algorithm)
            print("System initialized successfully!")
            
        except (ValueError, IndexError) as e:
            print(f"Invalid input: {e}")
    
    def _add_aircraft_menu(self):
        """Add aircraft with user input."""
        if not self.airport:
            print("Please initialize the system first.")
            return
        
        try:
            print("\nAircraft Types:")
            aircraft_types = list(AircraftType)
            for i, aircraft_type in enumerate(aircraft_types, 1):
                print(f"{i}. {aircraft_type.name}")
            
            type_choice = int(input("Select aircraft type (1-6): "))
            aircraft_type = aircraft_types[type_choice - 1]
            
            operation = input("Operation (landing/takeoff, default landing): ").strip() or "landing"
            emergency = input("Emergency? (y/n, default n): ").strip().lower() == 'y'
            fuel_level = float(input("Fuel level (0-100, default 50): ") or "50")
            
            aircraft_id = self.airport.add_aircraft(aircraft_type, operation, emergency, fuel_level)
            print(f"Aircraft {aircraft_id} added successfully!")
            
        except (ValueError, IndexError) as e:
            print(f"Invalid input: {e}")
    
    def _view_status(self):
        """View current system status."""
        if not self.airport:
            print("Please initialize the system first.")
            return
        
        status = self.airport.get_detailed_status()
        
        print("\n" + "="*50)
        print("CURRENT SYSTEM STATUS")
        print("="*50)
        
        print(f"Simulation Time: {status['simulation_time']}")
        print(f"Algorithm: {status['queues']['algorithm']}")
        
        print("\nRunway Status:")
        for runway in status['runways']:
            print(f"  {runway['id']}: {runway['status']}")
            if runway['current_aircraft']:
                print(f"    Aircraft: {runway['current_aircraft']}")
                print(f"    Remaining: {runway['remaining_time']:.1f}s")
        
        print(f"\nQueue Status:")
        print(f"  Landing Queue: {status['queues']['landing_queue_size']} aircraft")
        print(f"  Takeoff Queue: {status['queues']['takeoff_queue_size']} aircraft")
        print(f"  Emergency Queue: {status['queues']['emergency_queue_size']} aircraft")
        
        print(f"\nStatistics:")
        stats = status['statistics']
        print(f"  Total Operations: {stats['total_operations']}")
        print(f"  Successful Operations: {stats['successful_operations']}")
        print(f"  Deadlock Events: {stats['deadlock_events']}")
        
        if status['deadlock_status']['has_deadlock']:
            print("\n⚠️  DEADLOCK DETECTED!")
            print(f"   Processes in deadlock: {len(status['deadlock_status']['processes_in_deadlock'])}")
    
    def _run_simulation_step(self):
        """Run one simulation step."""
        if not self.airport:
            print("Please initialize the system first.")
            return
        
        self.airport.run_simulation_step()
        print("Simulation step completed.")
    
    def _change_algorithm(self):
        """Change scheduling algorithm."""
        if not self.airport:
            print("Please initialize the system first.")
            return
        
        print("\nAvailable algorithms:")
        algorithms = list(SchedulingAlgorithm)
        for i, alg in enumerate(algorithms, 1):
            print(f"{i}. {alg.value}")
        
        try:
            choice = int(input("Select new algorithm (1-4): "))
            algorithm = algorithms[choice - 1]
            self.airport.change_scheduling_algorithm(algorithm)
            print(f"Algorithm changed to: {algorithm.value}")
        except (ValueError, IndexError) as e:
            print(f"Invalid input: {e}")
    
    def _run_auto_simulation(self):
        """Run automatic simulation."""
        if not self.airport:
            print("Please initialize the system first.")
            return
        
        try:
            duration = int(input("Enter simulation duration (steps, default 50): ") or "50")
            print(f"Running automatic simulation for {duration} steps...")
            
            self.airport.start_simulation()
            
            for step in range(duration):
                # Add random aircraft
                if random.random() < 0.3:  # 30% chance
                    aircraft_type = random.choice(list(AircraftType))
                    operation_type = random.choice(["landing", "takeoff"])
                    emergency = random.random() < 0.1  # 10% emergency
                    fuel_level = random.uniform(10, 100)
                    
                    aircraft_id = self.airport.add_aircraft(aircraft_type, operation_type, emergency, fuel_level)
                    print(f"Added aircraft: {aircraft_id}")
                
                self.airport.run_simulation_step()
                
                # Show status every 10 steps
                if step % 10 == 0:
                    status = self.airport.get_system_status()
                    print(f"Step {step}: Queues - L:{status['queues']['landing_queue_size']}, "
                          f"T:{status['queues']['takeoff_queue_size']}, "
                          f"E:{status['queues']['emergency_queue_size']}")
            
            self.airport.stop_simulation()
            print("Automatic simulation completed!")
            
        except ValueError:
            print("Invalid input.")
    
    def _run_comprehensive_test(self):
        """Run comprehensive test suite."""
        if not self.simulation:
            print("Please initialize the system first.")
            return
        
        print("Running comprehensive test suite...")
        results = self.simulation.run_comprehensive_test()
        print("Comprehensive test completed!")
    
    def _generate_report(self):
        """Generate and display report."""
        if not self.airport:
            print("Please initialize the system first.")
            return
        
        report = self.airport.generate_report()
        print(report)
        
        # Save report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"airport_report_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write(report)
        
        print(f"Report saved to {filename}")
    
    def run_demo_scenario(self):
        """Run a predefined demo scenario."""
        print("\n" + "="*60)
        print("RUNNING DEMO SCENARIO")
        print("="*60)
        
        # Initialize system
        self.initialize_system(3, SchedulingAlgorithm.PRIORITY)
        
        # Add some aircraft
        print("\nAdding aircraft to the system...")
        
        # Emergency aircraft
        self.airport.add_aircraft(AircraftType.EMERGENCY, "landing", True, 5.0)
        print("Added emergency aircraft with low fuel")
        
        # Commercial aircraft
        for i in range(3):
            self.airport.add_aircraft(AircraftType.COMMERCIAL, "landing", False, 50.0)
        print("Added 3 commercial aircraft")
        
        # Military aircraft
        self.airport.add_aircraft(AircraftType.MILITARY, "takeoff", False, 80.0)
        print("Added military aircraft")
        
        # Private aircraft
        self.airport.add_aircraft(AircraftType.PRIVATE, "landing", False, 30.0)
        print("Added private aircraft")
        
        # Run simulation
        print("\nRunning simulation...")
        self.airport.start_simulation()
        
        for step in range(20):
            self.airport.run_simulation_step()
            
            if step % 5 == 0:
                status = self.airport.get_system_status()
                print(f"Step {step}: Operations completed: {status['statistics']['successful_operations']}")
        
        self.airport.stop_simulation()
        
        # Show final report
        print("\nFinal Report:")
        report = self.airport.generate_report()
        print(report)

def main():
    """Main function to run the application."""
    app = AirportSchedulingApp()
    
    print("Welcome to Airport Runway Scheduling System!")
    print("This system demonstrates priority scheduling and deadlock prevention.")
    
    while True:
        print("\nMain Menu:")
        print("1. Interactive Demo")
        print("2. Run Demo Scenario")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == '1':
            app.interactive_demo()
        elif choice == '2':
            app.run_demo_scenario()
        elif choice == '3':
            print("Thank you for using Airport Runway Scheduling System!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()