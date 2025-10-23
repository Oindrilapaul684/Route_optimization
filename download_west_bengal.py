#!/usr/bin/env python3
"""
West Bengal Map Downloader - Standalone Version
Download real city maps from OpenStreetMap for West Bengal cities
"""

import os
import requests
import argparse
import sys

# West Bengal Cities Coordinates
WEST_BENGAL_CITIES = {
    "kolkata": (22.5726, 88.3639),
    "durgapur": (23.5204, 87.3119),
    "asansol": (23.6739, 86.9524),
    "siliguri": (26.7271, 88.3953),
    "howrah": (22.5958, 88.2636),
    "kharagpur": (22.3460, 87.2320),
    "bardhaman": (23.2400, 87.8700),
    "malda": (25.0119, 88.1423),
    "jalpaiguri": (26.5432, 88.7192),
    "coochbehar": (26.3238, 89.4520),
    "saltlake": (22.5900, 88.4100),
    "newtown": (22.5800, 88.4800),
}

class SimpleMapDownloader:
    def __init__(self):
        self.base_url = "http://overpass-api.de/api/map"
        self.cities_dir = "city_maps/real_cities"
        os.makedirs(self.cities_dir, exist_ok=True)
    
    def download_city(self, city_name: str, area_size_km: float = 4.0) -> str:
        """Download city map by name"""
        city_name_lower = city_name.lower()
        
        if city_name_lower not in WEST_BENGAL_CITIES:
            print(f"❌ City '{city_name}' not found in West Bengal database")
            print(f"💡 Available cities: {list(WEST_BENGAL_CITIES.keys())}")
            return None
        
        base_lat, base_lon = WEST_BENGAL_CITIES[city_name_lower]
        
        # Calculate bounding box
        lat_offset = (area_size_km / 111.0) / 2
        lon_offset = (area_size_km / (111.0 * abs(base_lat))) / 2
        
        bbox = (
            base_lat - lat_offset,
            base_lon - lon_offset,
            base_lat + lat_offset,
            base_lon + lon_offset
        )
        
        return self.download_by_bbox(city_name, bbox)
    
    def download_by_bbox(self, city_name: str, bbox: tuple) -> str:
        """Download map by bounding box"""
        print(f"🗺️ Downloading {city_name} map data...")
        
        min_lat, min_lon, max_lat, max_lon = bbox
        osm_file = os.path.join(self.cities_dir, f"{city_name}.osm")
        
        # Overpass API query
        query = f"?bbox={min_lon},{min_lat},{max_lon},{max_lat}"
        url = self.base_url + query
        
        try:
            print(f"🌐 Downloading from: {url}")
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            with open(osm_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            file_size = os.path.getsize(osm_file) / 1024
            print(f"✅ Successfully downloaded {city_name} map ({file_size:.1f} KB)")
            return osm_file
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to download {city_name}: {e}")
            return None
    
    def convert_to_sumo(self, osm_file: str) -> str:
        """Convert OSM file to SUMO network"""
        if not os.path.exists(osm_file):
            print(f"❌ OSM file not found: {osm_file}")
            return None
        
        city_name = os.path.basename(osm_file).replace('.osm', '')
        net_file = os.path.join(self.cities_dir, f"{city_name}.net.xml")
        
        print(f"🔄 Converting {city_name} OSM to SUMO network...")
        
        # Use netconvert to convert OSM to SUMO network
        cmd = f"netconvert --osm-files {osm_file} --output-file {net_file}"
        result = os.system(cmd)
        
        if result == 0 and os.path.exists(net_file):
            print(f"✅ Successfully converted to SUMO network: {net_file}")
            return net_file
        else:
            print(f"❌ Failed to convert OSM to SUMO network")
            return None
    
    def validate_network(self, net_file: str) -> bool:
        """Validate the generated SUMO network"""
        if not os.path.exists(net_file):
            return False
        
        try:
            # Try to import sumolib (check if SUMO is available)
            import sumolib
            net = sumolib.net.readNet(net_file)
            edge_count = len([edge for edge in net.getEdges() if edge.getFunction() == ''])
            
            print(f"📊 Network stats: {edge_count} roads, {len(net.getNodes())} intersections")
            
            if edge_count > 10:
                return True
            else:
                print("⚠️ Network seems too small, might not be usable")
                return False
                
        except ImportError:
            print("⚠️ SUMO not available for validation, but network file was created")
            return True
        except Exception as e:
            print(f"❌ Network validation failed: {e}")
            return False

def list_west_bengal_cities():
    """List all West Bengal cities"""
    print("🏙️ West Bengal Cities Available:")
    print("=" * 50)
    for city, coords in WEST_BENGAL_CITIES.items():
        # Check if the city map already exists
        net_file = f"city_maps/real_cities/{city}.net.xml"
        exists = "✅" if os.path.exists(net_file) else "❌"
        print(f"  {exists} {city:15} - Latitude: {coords[0]:.4f}, Longitude: {coords[1]:.4f}")
    print(f"\n💡 Download with: python download_west_bengal.py <city_name>")

def main():
    parser = argparse.ArgumentParser(
        description='Download real city maps for West Bengal cities',
        epilog='''
Examples:
  python download_west_bengal.py kolkata
  python download_west_bengal.py durgapur --size 5.0
  python download_west_bengal.py --list-cities
        '''
    )
    
    parser.add_argument('city', nargs='?', help='City name to download')
    parser.add_argument('--list-cities', action='store_true', help='List West Bengal cities')
    parser.add_argument('--size', type=float, default=4.0, help='Area size in km (default: 4.0)')
    parser.add_argument('--no-convert', action='store_true', help='Download OSM only')
    
    args = parser.parse_args()
    
    print("🗺️  West Bengal Map Downloader")
    print("=" * 40)
    
    if args.list_cities:
        list_west_bengal_cities()
        return
    
    if not args.city:
        print("❌ Please specify a city name")
        print("💡 Use --list-cities to see available cities")
        print("💡 Example: python download_west_bengal.py kolkata")
        return
    
    downloader = SimpleMapDownloader()
    
    # Download the city
    osm_file = downloader.download_city(args.city, args.size)
    
    if not osm_file:
        print("❌ Failed to download map data")
        sys.exit(1)
    
    if not args.no_convert:
        net_file = downloader.convert_to_sumo(osm_file)
        if net_file and downloader.validate_network(net_file):
            print(f"🎉 Success! Your {args.city} map is ready: {net_file}")
            print(f"💡 You can now use this map in the route optimization assistant!")
        else:
            print("❌ Failed to create usable SUMO network")
            sys.exit(1)
    else:
        print(f"🎉 OSM file downloaded: {osm_file}")

if __name__ == "__main__":
    main()