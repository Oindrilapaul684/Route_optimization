import traci
import sumolib
import numpy as np
import os
import random
from typing import List, Dict

class CityTrafficManager:
    def __init__(self, net_file: str, config: dict):
        self.net_file = net_file
        self.config = config
        
        try:
            self.net = sumolib.net.readNet(net_file)
            self.is_real_city = 'real_cities' in net_file
            city_name = os.path.basename(net_file).replace('.net.xml', '')
            print(f"📍 Loaded {'real' if self.is_real_city else 'simulated'} city: {city_name}")
        except Exception as e:
            print(f"⚠️ Could not load network: {e}")
            self.is_real_city = False
            
        self.simulation_active = False
    
    def generate_realistic_routes(self, output_file: str):
        """Generate realistic routes for the city"""
        edges = [edge.getID() for edge in self.net.getEdges() if edge.getFunction() == '']
        
        routes_content = """<?xml version="1.0" encoding="UTF-8"?>
<routes>
    <vType id="car" accel="2.6" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="55" guiShape="passenger"/>
    <vType id="bus" accel="1.5" decel="3.0" sigma="0.5" length="12" minGap="3" maxSpeed="35" guiShape="bus"/>
    <vType id="truck" accel="1.3" decel="2.5" sigma="0.5" length="16" minGap="3" maxSpeed="25" guiShape="truck"/>
    <vType id="motorcycle" accel="3.0" decel="6.0" sigma="0.8" length="2" minGap="1" maxSpeed="60" guiShape="motorcycle"/>
"""
        
        vehicle_types = ["car", "bus", "truck", "motorcycle"]
        type_weights = [0.75, 0.08, 0.07, 0.10]  # Realistic distribution
        
        for i in range(self.config.get('num_vehicles', 40)):
            veh_type = random.choices(vehicle_types, weights=type_weights)[0]
            depart = random.randint(0, 900)  # Stagger over 15 minutes
            
            start_edge = random.choice(edges)
            end_edge = random.choice(edges)
            
            while end_edge == start_edge:
                end_edge = random.choice(edges)
            
            try:
                route = self.net.getShortestPath(
                    self.net.getEdge(start_edge), 
                    self.net.getEdge(end_edge)
                )[0]
                route_edges = " ".join([edge.getID() for edge in route])
                
                routes_content += f'''
    <vehicle id="veh{i}" type="{veh_type}" depart="{depart}" color="{self._get_vehicle_color(veh_type)}">
        <route edges="{route_edges}"/>
    </vehicle>'''
                
            except Exception as e:
                # Fallback to direct route
                routes_content += f'''
    <vehicle id="veh{i}" type="{veh_type}" depart="{depart}" color="{self._get_vehicle_color(veh_type)}">
        <route edges="{start_edge} {end_edge}"/>
    </vehicle>'''
        
        routes_content += "\n</routes>"
        
        with open(output_file, 'w') as f:
            f.write(routes_content)
        
        print(f"✅ Generated routes for {self.config.get('num_vehicles', 40)} vehicles")
        return output_file
    
    def _get_vehicle_color(self, vehicle_type: str) -> str:
        """Get realistic vehicle colors"""
        colors = {
            "car": "0.2,0.2,0.8",      # Blue
            "bus": "0.8,0.2,0.2",      # Red
            "truck": "0.3,0.3,0.3",    # Dark gray
            "motorcycle": "0.9,0.7,0.1" # Gold
        }
        return colors.get(vehicle_type, "0.5,0.5,0.5")
    
    def start_simulation(self, route_file: str):
        """Start SUMO simulation"""
        sumo_binary = "sumo-gui" if self.config.get('gui', True) else "sumo"
        sumo_cmd = [
            sumo_binary,
            '-n', self.net_file,
            '-r', route_file,
            '--waiting-time-memory', '1000',
            '--time-to-teleport', '-1'
        ]
        
        traci.start(sumo_cmd)
        self.simulation_active = True
        print("🚗 SUMO simulation started!")
    
    def stop_simulation(self):
        """Stop SUMO simulation"""
        if self.simulation_active:
            traci.close()
            self.simulation_active = False
            print("🛑 SUMO simulation stopped")