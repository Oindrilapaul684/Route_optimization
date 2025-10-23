#!/usr/bin/env python3
"""
Create default network for the route optimization project
"""

import os

def create_default_network():
    """Create a default grid network"""
    print("🏗️ Creating default city network...")
    
    os.makedirs('city_maps', exist_ok=True)
    
    # Create a simple grid network
    result = os.system(
        "netgenerate --grid --grid.number=6 --grid.length=150 " +
        "--output-file=city_maps/downtown.net.xml"
    )
    
    if result == 0 and os.path.exists('city_maps/downtown.net.xml'):
        print("✅ Successfully created default network: city_maps/downtown.net.xml")
        return True
    else:
        print("❌ Failed to create default network")
        return False

if __name__ == "__main__":
    create_default_network()