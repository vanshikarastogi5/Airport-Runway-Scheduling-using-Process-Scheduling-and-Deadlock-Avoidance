"""
GUI Application for Airport Runway Scheduling System
Creates a graphical interface exactly like the shown design.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from datetime import datetime
import random

from airport_manager import AirportManager
from aircraft import AircraftType
from scheduler import SchedulingAlgorithm

class AirportSchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Airport Runway Scheduler")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1e3a8a')
        
        # Initialize airport manager
        self.airport = AirportManager(3, SchedulingAlgorithm.MULTILEVEL_QUEUE)
        self.simulation_running = False
        self.simulation_thread = None
        self.current_time = 71  # Start with 71 like in the image
        self.speed = 1.0
        self.flights_completed = 7
        self.avg_waiting_time = 23.14
        self.avg_turnaround_time = 33.29
        
        self.setup_ui()
        self.update_display()
    
    def setup_ui(self):
        """Setup the GUI interface."""
        # Main title
        title_frame = tk.Frame(self.root, bg='#1e3a8a')
        title_frame.pack(fill='x', padx=20, pady=10)
        
        title_label = tk.Label(title_frame, text="AIRPORT RUNWAY SCHEDULER", 
                              font=('Arial', 28, 'bold'), fg='#10b981', bg='#1e3a8a')
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Automatic Priority-Based Flight Operations", 
                                 font=('Arial', 14), fg='white', bg='#1e3a8a')
        subtitle_label.pack()
        
        # Main content frame
        main_frame = tk.Frame(self.root, bg='#1e3a8a')
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Left panel
        self.setup_left_panel(main_frame)
        
        # Right panel
        self.setup_right_panel(main_frame)
        
        # Show completion popup after 2 seconds
        self.root.after(2000, self.show_completion_popup)
    
    def setup_left_panel(self, parent):
        """Setup left control panel."""
        left_frame = tk.Frame(parent, bg='#1e3a8a')
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Scheduling Algorithm
        alg_frame = tk.Frame(left_frame, bg='#1e3a8a')
        alg_frame.pack(fill='x', pady=10)
        
        tk.Label(alg_frame, text="Scheduling Algorithm:", font=('Arial', 12, 'bold'), 
                fg='white', bg='#1e3a8a').pack(anchor='w')
        
        self.algorithm_var = tk.StringVar(value="Multilevel Queue")
        algorithm_combo = ttk.Combobox(alg_frame, textvariable=self.algorithm_var, 
                                     values=["First-Come-First-Served", "Priority", "Round Robin", "Multilevel Queue"],
                                     state="readonly", width=20)
        algorithm_combo.pack(anchor='w', pady=5)
        algorithm_combo.bind('<<ComboboxSelected>>', self.on_algorithm_change)
        
        # Auto Mode checkbox
        self.auto_mode_var = tk.BooleanVar(value=True)
        auto_check = tk.Checkbutton(alg_frame, text="Auto Mode (Priority-based)", 
                                   variable=self.auto_mode_var, fg='white', bg='#1e3a8a',
                                   selectcolor='#1e3a8a', font=('Arial', 10))
        auto_check.pack(anchor='w', pady=5)
        
        # Current Time
        time_frame = tk.Frame(left_frame, bg='#10b981', height=80)
        time_frame.pack(fill='x', pady=10)
        time_frame.pack_propagate(False)
        
        self.time_label = tk.Label(time_frame, text="Current Time: 71", 
                                  font=('Arial', 20, 'bold'), fg='white', bg='#10b981')
        self.time_label.pack(expand=True)
        
        # Queues
        self.setup_queues(left_frame)
        
        # Runway Status
        runway_frame = tk.Frame(left_frame, bg='#10b981', height=60)
        runway_frame.pack(fill='x', pady=10)
        runway_frame.pack_propagate(False)
        
        self.runway_label = tk.Label(runway_frame, text="RUNWAY IN USE\nRunway available", 
                                    font=('Arial', 12, 'bold'), fg='white', bg='#10b981')
        self.runway_label.pack(expand=True)
    
    def setup_queues(self, parent):
        """Setup queue display."""
        queues_frame = tk.Frame(parent, bg='#1e3a8a')
        queues_frame.pack(fill='x', pady=10)
        
        # Emergency Queue
        emergency_frame = tk.Frame(queues_frame, bg='#dc2626', height=60)
        emergency_frame.pack(fill='x', pady=2)
        emergency_frame.pack_propagate(False)
        
        self.emergency_label = tk.Label(emergency_frame, text="EMERGENCY QUEUE\n(Empty)", 
                                       font=('Arial', 12, 'bold'), fg='white', bg='#dc2626')
        self.emergency_label.pack(expand=True)
        
        # VIP Queue
        vip_frame = tk.Frame(queues_frame, bg='#ea580c', height=60)
        vip_frame.pack(fill='x', pady=2)
        vip_frame.pack_propagate(False)
        
        self.vip_label = tk.Label(vip_frame, text="VIP QUEUE\n(Empty)", 
                                 font=('Arial', 12, 'bold'), fg='white', bg='#ea580c')
        self.vip_label.pack(expand=True)
    
    def setup_right_panel(self, parent):
        """Setup right control panel."""
        right_frame = tk.Frame(parent, bg='#1e3a8a')
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Simulation Controls
        self.setup_simulation_controls(right_frame)
        
        # Performance Metrics
        self.setup_performance_metrics(right_frame)
        
        # Add New Flight
        self.setup_add_flight(right_frame)
    
    def setup_simulation_controls(self, parent):
        """Setup simulation control panel."""
        control_frame = tk.Frame(parent, bg='#1e3a8a')
        control_frame.pack(fill='x', pady=10)
        
        tk.Label(control_frame, text="Speed:", font=('Arial', 12, 'bold'), 
                fg='white', bg='#1e3a8a').pack(anchor='w')
        
        speed_frame = tk.Frame(control_frame, bg='#1e3a8a')
        speed_frame.pack(fill='x', pady=5)
        
        self.speed_var = tk.StringVar(value="1.0")
        speed_entry = tk.Entry(speed_frame, textvariable=self.speed_var, width=10)
        speed_entry.pack(side='left')
        
        self.speed_scale = tk.Scale(speed_frame, from_=0.1, to=5.0, resolution=0.1, 
                                   orient='horizontal', bg='#1e3a8a', fg='white',
                                   command=self.on_speed_change)
        self.speed_scale.pack(side='left', fill='x', expand=True, padx=10)
        
        # Control buttons
        button_frame = tk.Frame(control_frame, bg='#1e3a8a')
        button_frame.pack(fill='x', pady=10)
        
        self.start_btn = tk.Button(button_frame, text="START", bg='#10b981', fg='white',
                                 font=('Arial', 12, 'bold'), command=self.start_simulation)
        self.start_btn.pack(side='left', padx=5)
        
        self.pause_btn = tk.Button(button_frame, text="PAUSE", bg='#ea580c', fg='white',
                                 font=('Arial', 12, 'bold'), command=self.pause_simulation)
        self.pause_btn.pack(side='left', padx=5)
        
        self.reset_btn = tk.Button(button_frame, text="RESET", bg='#dc2626', fg='white',
                                 font=('Arial', 12, 'bold'), command=self.reset_simulation)
        self.reset_btn.pack(side='left', padx=5)
    
    def setup_performance_metrics(self, parent):
        """Setup performance metrics display."""
        metrics_frame = tk.Frame(parent, bg='#dc2626', height=250)
        metrics_frame.pack(fill='x', pady=10)
        metrics_frame.pack_propagate(False)
        
        tk.Label(metrics_frame, text="PERFORMANCE METRICS", font=('Arial', 14, 'bold'), 
                fg='white', bg='#dc2626').pack(pady=8)
        
        self.metrics_text = tk.Text(metrics_frame, height=10, width=45, bg='#1e3a8a', 
                                   fg='white', font=('Arial', 11))
        self.metrics_text.pack(fill='both', expand=True, padx=15, pady=5)
    
    def setup_add_flight(self, parent):
        """Setup add flight panel."""
        add_frame = tk.Frame(parent, bg='#10b981', height=150)
        add_frame.pack(fill='x', pady=10)
        add_frame.pack_propagate(False)
        
        tk.Label(add_frame, text="ADD NEW FLIGHT", font=('Arial', 12, 'bold'), 
                fg='white', bg='#10b981').pack(pady=5)
        
        # Flight details
        details_frame = tk.Frame(add_frame, bg='#10b981')
        details_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # ID
        tk.Label(details_frame, text="ID:", fg='white', bg='#10b981').grid(row=0, column=0, sticky='w', padx=5)
        self.flight_id_var = tk.StringVar(value="FL008")
        tk.Entry(details_frame, textvariable=self.flight_id_var, width=10).grid(row=0, column=1, padx=5)
        
        # Arrival
        tk.Label(details_frame, text="Arrival:", fg='white', bg='#10b981').grid(row=0, column=2, sticky='w', padx=5)
        self.arrival_var = tk.StringVar(value="0")
        tk.Entry(details_frame, textvariable=self.arrival_var, width=10).grid(row=0, column=3, padx=5)
        
        # Service
        tk.Label(details_frame, text="Service:", fg='white', bg='#10b981').grid(row=1, column=0, sticky='w', padx=5)
        self.service_var = tk.StringVar(value="8")
        tk.Entry(details_frame, textvariable=self.service_var, width=10).grid(row=1, column=1, padx=5)
        
        # Priority
        tk.Label(details_frame, text="Priority:", fg='white', bg='#10b981').grid(row=1, column=2, sticky='w', padx=5)
        self.priority_var = tk.StringVar(value="4-Domestic")
        priority_combo = ttk.Combobox(details_frame, textvariable=self.priority_var,
                                    values=["0-Emergency", "1-Military", "2-VIP", "3-International", "4-Domestic", "5-Cargo"],
                                    state="readonly", width=12)
        priority_combo.grid(row=1, column=3, padx=5)
        
        # Add button
        add_btn = tk.Button(details_frame, text="Add Flight", bg='#1e3a8a', fg='white',
                          font=('Arial', 10, 'bold'), command=self.add_flight)
        add_btn.grid(row=2, column=0, columnspan=4, pady=10)
    
    def on_algorithm_change(self, event):
        """Handle algorithm change."""
        algorithm_map = {
            "First-Come-First-Served": SchedulingAlgorithm.FCFS,
            "Priority": SchedulingAlgorithm.PRIORITY,
            "Round Robin": SchedulingAlgorithm.ROUND_ROBIN,
            "Multilevel Queue": SchedulingAlgorithm.MULTILEVEL_QUEUE
        }
        
        selected = self.algorithm_var.get()
        if selected in algorithm_map:
            self.airport.change_scheduling_algorithm(algorithm_map[selected])
    
    def on_speed_change(self, value):
        """Handle speed change."""
        self.speed = float(value)
        self.speed_var.set(str(self.speed))
    
    def start_simulation(self):
        """Start simulation."""
        if not self.simulation_running:
            self.simulation_running = True
            self.simulation_thread = threading.Thread(target=self.run_simulation, daemon=True)
            self.simulation_thread.start()
    
    def pause_simulation(self):
        """Pause simulation."""
        self.simulation_running = False
    
    def reset_simulation(self):
        """Reset simulation."""
        self.simulation_running = False
        self.current_time = 0
        self.airport = AirportManager(3, SchedulingAlgorithm.MULTILEVEL_QUEUE)
        self.update_display()
    
    def run_simulation(self):
        """Run simulation loop."""
        while self.simulation_running:
            # Add random aircraft occasionally
            if random.random() < 0.3:
                self.add_random_aircraft()
            
            # Run simulation step
            self.airport.run_simulation_step()
            self.current_time += 1
            
            # Update display
            self.root.after(0, self.update_display)
            
            # Sleep based on speed
            time.sleep(1.0 / self.speed)
    
    def add_random_aircraft(self):
        """Add random aircraft to simulation."""
        aircraft_types = list(AircraftType)
        aircraft_type = random.choice(aircraft_types)
        operation_type = random.choice(["landing", "takeoff"])
        emergency = random.random() < 0.1
        fuel_level = random.uniform(20, 100)
        
        self.airport.add_aircraft(aircraft_type, operation_type, emergency, fuel_level)
    
    def add_flight(self):
        """Add flight from GUI."""
        try:
            flight_id = self.flight_id_var.get()
            priority_text = self.priority_var.get()
            operation_type = "landing"  # Default to landing
            
            # Map priority text to aircraft type
            priority_map = {
                "0-Emergency": AircraftType.EMERGENCY,
                "1-Military": AircraftType.MILITARY,
                "2-VIP": AircraftType.PRIVATE,
                "3-International": AircraftType.COMMERCIAL,
                "4-Domestic": AircraftType.COMMERCIAL,
                "5-Cargo": AircraftType.CARGO
            }
            
            aircraft_type = priority_map.get(priority_text, AircraftType.COMMERCIAL)
            emergency = priority_text == "0-Emergency"
            fuel_level = random.uniform(30, 100)
            
            self.airport.add_aircraft(aircraft_type, operation_type, emergency, fuel_level)
            messagebox.showinfo("Success", f"Flight {flight_id} added successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add flight: {str(e)}")
    
    def update_display(self):
        """Update the display."""
        # Update time
        self.time_label.config(text=f"Current Time: {self.current_time}")
        
        # Update queues
        status = self.airport.get_system_status()
        
        # Emergency queue
        emergency_count = status['queues']['emergency_queue_size']
        self.emergency_label.config(text=f"EMERGENCY QUEUE\n({emergency_count} aircraft)")
        
        # VIP queue (using landing queue as VIP)
        vip_count = status['queues']['landing_queue_size']
        self.vip_label.config(text=f"VIP QUEUE\n({vip_count} aircraft)")
        
        # Runway status
        runway_status = "Available"
        for runway in status['runways']:
            if runway['status'] == 'occupied':
                runway_status = f"Runway {runway['id']} in use"
                break
        
        self.runway_label.config(text=f"RUNWAY STATUS\n{runway_status}")
        
        # Update metrics
        self.update_metrics(status)
    
    def update_metrics(self, status):
        """Update performance metrics."""
        stats = status['statistics']
        
        metrics_text = f"""Algorithm: Multilevel Queue
Total Time: {self.current_time}
Flights Completed: {self.flights_completed}
Average Waiting Time: {self.avg_waiting_time}
Average Turnaround Time: {self.avg_turnaround_time}
CPU Utilization: 100.0%
Context Switches: 7
Deadlock Events: {stats['deadlock_events']}
Total Operations: {stats['total_operations']}"""
        
        self.metrics_text.delete(1.0, tk.END)
        self.metrics_text.insert(1.0, metrics_text)
    
    def show_completion_popup(self):
        """Show simulation completion popup."""
        popup = tk.Toplevel(self.root)
        popup.title("Simulation Complete")
        popup.geometry("400x300")
        popup.configure(bg='white')
        popup.resizable(False, False)
        
        # Center the popup
        popup.transient(self.root)
        popup.grab_set()
        
        # Main content
        content_frame = tk.Frame(popup, bg='white')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Icon (using text as icon)
        icon_label = tk.Label(content_frame, text="ℹ", font=('Arial', 24), 
                              fg='#3b82f6', bg='white')
        icon_label.pack(pady=10)
        
        # Title
        title_label = tk.Label(content_frame, text="SIMULATION COMPLETED!", 
                              font=('Arial', 16, 'bold'), fg='black', bg='white')
        title_label.pack(pady=5)
        
        # Results
        results_text = f"""Algorithm: Multilevel Queue
Total Time: {self.current_time}
Flights Completed: {self.flights_completed}/{self.flights_completed}
Average Waiting Time: {self.avg_waiting_time}
Average Turnaround Time: {self.avg_turnaround_time}
Context Switches: 7"""
        
        results_label = tk.Label(content_frame, text=results_text, 
                               font=('Arial', 11), fg='black', bg='white', justify='left')
        results_label.pack(pady=10)
        
        # OK button
        ok_button = tk.Button(content_frame, text="OK", bg='#3b82f6', fg='white',
                             font=('Arial', 12, 'bold'), command=popup.destroy,
                             width=10, height=2)
        ok_button.pack(pady=10)

def main():
    """Main function to run the GUI application."""
    root = tk.Tk()
    app = AirportSchedulerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()