# generate_routes.py
import os
import random

def create_simple_routes(net_file="city_maps/downtown.net.xml", output_file="city_maps/simple_routes.rou.xml"):
    """Create a simple route file for testing"""
    
    print("🚗 Creating simple vehicle routes...")
    
    routes_content = """<?xml version="1.0" encoding="UTF-8"?>
<routes>
    <vType id="car" accel="2.6" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="13.89" guiShape="passenger"/>
    <vType id="bus" accel="1.5" decel="3.0" sigma="0.5" length="12" minGap="3" maxSpeed="11.11" guiShape="bus"/>
    
    <!-- Simple routes for testing -->
    <vehicle id="veh0" type="car" depart="0">
        <route edges="1to2 2to3"/>
    </vehicle>
    
    <vehicle id="veh1" type="car" depart="5">
        <route edges="1to4 4to7"/>
    </vehicle>
    
    <vehicle id="veh2" type="bus" depart="10">
        <route edges="2to5 5to8"/>
    </vehicle>
    
    <vehicle id="veh3" type="car" depart="15">
        <route edges="3to6 6to9"/>
    </vehicle>
    
    <vehicle id="veh4" type="car" depart="20">
        <route edges="4to5 5to6"/>
    </vehicle>
    
    <vehicle id="veh5" type="car" depart="25">
        <route edges="7to8 8to9"/>
    </vehicle>
    
    <vehicle id="veh6" type="bus" depart="30">
        <route edges="1to2 2to5 5to8"/>
    </vehicle>
    
    <vehicle id="veh7" type="car" depart="35">
        <route edges="4to5 5to2 2to3"/>
    </vehicle>
    
    <vehicle id="veh8" type="car" depart="40">
        <route edges="7to8 8to5 5to6"/>
    </vehicle>
    
    <vehicle id="veh9" type="car" depart="45">
        <route edges="1to4 4to5 5to6 6to9"/>
    </vehicle>
</routes>"""
    
    with open(output_file, 'w') as f:
        f.write(routes_content)
    
    print(f"✅ Created {output_file} with 10 vehicles")
    return True

if __name__ == "__main__":
    create_simple_routes()