# test_simulation.py
import os
import sys

def test_sumo_simulation():
    """Test if SUMO simulation works with vehicles"""
    
    print("🧪 Testing SUMO Simulation...")
    
    # First, create a simple network if it doesn't exist
    if not os.path.exists("city_maps/downtown.net.xml"):
        print("📝 Creating test network...")
        os.system("netgenerate --grid --grid.number=4 --grid.length=100 --output-file=city_maps/downtown.net.xml")
    
    # Create simple routes
    print("🚗 Creating test routes...")
    routes_content = """<?xml version="1.0" encoding="UTF-8"?>
<routes>
    <vType id="car" accel="2.6" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="13.89"/>
    <vehicle id="test_veh" type="car" depart="0">
        <route edges="1to2"/>
    </vehicle>
</routes>"""
    
    with open("city_maps/test_routes.rou.xml", 'w') as f:
        f.write(routes_content)
    
    # Test the simulation
    try:
        import traci
        
        print("🚀 Starting SUMO test...")
        traci.start([
            'sumo',
            '-n', 'city_maps/downtown.net.xml',
            '-r', 'city_maps/test_routes.rou.xml',
            '--time-to-teleport', '-1'
        ])
        
        # Run a few steps
        for step in range(50):
            traci.simulationStep()
            vehicles = traci.vehicle.getIDList()
            print(f"Step {step}: {len(vehicles)} vehicles")
            
            if vehicles:
                print(f"✅ SUCCESS: Vehicles detected! First vehicle: {vehicles[0]}")
                traci.close()
                return True
        
        print("❌ FAILED: No vehicles detected after 50 steps")
        traci.close()
        return False
        
    except Exception as e:
        print(f"❌ SUMO test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_sumo_simulation()
    if success:
        print("🎉 SUMO simulation test PASSED!")
    else:
        print("💡 SUMO simulation test FAILED!")