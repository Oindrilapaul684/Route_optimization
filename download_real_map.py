#!/usr/bin/env python3
"""
Real Map Downloader for Smart Route Assistant - West Bengal Edition
Download real city maps from OpenStreetMap for West Bengal cities
FIXED VERSION - No module import issues
"""

import os
import sys
import requests
import argparse
import time

# Add current directory to Python path to fix import issues
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# West Bengal Cities Coordinates with descriptions
WEST_BENGAL_CITIES = {
    "kolkata": {
        "coords": (22.5726, 88.3639),
        "description": "Kolkata - Capital City - Dense Urban Traffic"
    },
    "durgapur": {
        "coords": (23.5204, 87.3119),
        "description": "Durgapur - Industrial City - Mixed Traffic"
    },
    "asansol": {
        "coords": (23.6739, 86.9524),
        "description": "Asansol - Mining & Industrial - Heavy Vehicle Traffic"
    },
    "siliguri": {
        "coords": (26.7271, 88.3953),
        "description": "Siliguri - Gateway to Northeast - Strategic Corridor"
    },
    "howrah": {
        "coords": (22.5958, 88.2636),
        "description": "Howrah - Twin City of Kolkata - Bridge Traffic"
    },
    "kharagpur": {
        "coords": (22.3460, 87.2320),
        "description": "Kharagpur - Railway Town - Educational Hub"
    },
    "bardhaman": {
        "coords": (23.2400, 87.8700),
        "description": "Bardhaman - Agricultural Hub"
    },
    "malda": {
        "coords": (25.0119, 88.1423),
        "description": "Malda - Mango City"
    },
    "jalpaiguri": {
        "coords": (26.5432, 88.7192),
        "description": "Jalpaiguri - Tea Gardens"
    },
    "coochbehar": {
        "coords": (26.3238, 89.4520),
        "description": "Cooch Behar - Historical City"
    },
    "saltlake": {
        "coords": (22.5900, 88.4100),
        "description": "Salt Lake - Planned Township - Grid Layout"
    },
    "newtown": {
        "coords": (22.5800, 88.4800),
        "description": "New Town - IT Hub - Modern Infrastructure"
    },
    "haldia": {
        "coords": (22.0667, 88.0694),
        "description": "Haldia - Industrial Port City"
    },
    "bankura": {
        "coords": (23.2324, 87.0786),
        "description": "Bankura - Cultural Heritage City"
    },
    "purulia": {
        "coords": (23.3328, 86.3610),
        "description": "Purulia - Chhau Dance Hub"
    }
}

# West Bengal Regions
WEST_BENGAL_REGIONS = {
    "metro": {
        "bbox": (22.45, 88.20, 22.65, 88.50),
        "description": "Kolkata Metropolitan Area - Dense Urban Network"
    },
    "industrial": {
        "bbox": (23.45, 86.90, 23.75, 87.35),
        "description": "Durgapur-Asansol Industrial Corridor"
    },
    "siliguri": {
        "bbox": (26.65, 88.25, 26.80, 88.50),
        "description": "Siliguri Corridor - Gateway to Northeast"
    },
    "north_bengal": {
        "bbox": (25.0, 87.0, 27.0, 89.0),
        "description": "North Bengal Region - Tea Gardens & Forests"
    }
}

class OSMDownloader:
    def __init__(self):
        self.base_url = "http://overpass-api.de/api/map"
        self.cities_dir = "city_maps/real_cities"
        os.makedirs(self.cities_dir, exist_ok=True)
        print(f"📁 Maps will be saved in: {os.path.abspath(self.cities_dir)}")
    
    def download_city_by_bbox(self, city_name: str, bbox: tuple) -> str:
        """
        Download city map by bounding box
        bbox format: (min_lat, min_lon, max_lat, max_lon)
        """
        print(f"🗺️ Downloading {city_name} map data...")
        
        min_lat, min_lon, max_lat, max_lon = bbox
        osm_file = os.path.join(self.cities_dir, f"{city_name}.osm")
        
        # Overpass API query
        query = f"?bbox={min_lon},{min_lat},{max_lon},{max_lat}"
        url = self.base_url + query
        
        try:
            print(f"🌐 Downloading from: {url}")
            print("⏳ This may take a few minutes depending on the area size...")
            
            response = requests.get(url, timeout=120)  # 2 minute timeout
            response.raise_for_status()
            
            with open(osm_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            file_size = os.path.getsize(osm_file) / 1024
            print(f"✅ Successfully downloaded {city_name} map ({file_size:.1f} KB)")
            return osm_file
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to download {city_name}: {e}")
            print("💡 Check your internet connection and try again")
            return None
    
    def download_city_by_name(self, city_name: str, area_size_km: float = 4.0) -> str:
        """
        Download city map by name
        area_size_km: approximate size of the area to download
        """
        city_name_lower = city_name.lower()
        
        if city_name_lower not in WEST_BENGAL_CITIES:
            print(f"❌ City '{city_name}' not found in West Bengal database")
            return None
        
        city_data = WEST_BENGAL_CITIES[city_name_lower]
        base_lat, base_lon = city_data["coords"]
        description = city_data["description"]
        
        print(f"📍 {description}")
        print(f"📡 Coordinates: {base_lat:.4f}, {base_lon:.4f}")
        print(f"📏 Area size: {area_size_km} km")
        
        # Calculate bounding box (rough conversion from km to degrees)
        lat_offset = (area_size_km / 111.0) / 2  # 1 degree ≈ 111 km
        lon_offset = (area_size_km / (111.0 * abs(base_lat))) / 2
        
        bbox = (
            base_lat - lat_offset,
            base_lon - lon_offset,
            base_lat + lat_offset,
            base_lon + lon_offset
        )
        
        return self.download_city_by_bbox(city_name, bbox)
    
    def convert_osm_to_sumo(self, osm_file: str) -> str:
        """Convert OSM file to SUMO network"""
        if not os.path.exists(osm_file):
            print(f"❌ OSM file not found: {osm_file}")
            return None
        
        city_name = os.path.basename(osm_file).replace('.osm', '')
        net_file = os.path.join(self.cities_dir, f"{city_name}.net.xml")
        
        print(f"🔄 Converting {city_name} OSM to SUMO network...")
        print("⏳ This may take a few minutes...")
        
        # Use netconvert to convert OSM to SUMO network
        cmd = f'netconvert --osm-files "{osm_file}" --output-file "{net_file}"'
        result = os.system(cmd)
        
        if result == 0 and os.path.exists(net_file):
            file_size = os.path.getsize(net_file) / 1024
            print(f"✅ Successfully converted to SUMO network: {net_file} ({file_size:.1f} KB)")
            return net_file
        else:
            print(f"❌ Failed to convert OSM to SUMO network")
            print("💡 Make sure SUMO is installed and available in PATH")
            return None
    
    def validate_network(self, net_file: str) -> bool:
        """Validate the generated SUMO network"""
        if not os.path.exists(net_file):
            return False
        
        try:
            # Try to import sumolib
            import sumolib
            net = sumolib.net.readNet(net_file)
            edges = [edge for edge in net.getEdges() if edge.getFunction() == '']
            edge_count = len(edges)
            node_count = len(net.getNodes())
            
            print(f"📊 Network Analysis:")
            print(f"   🛣️  Roads: {edge_count}")
            print(f"   🚦 Intersections: {node_count}")
            print(f"   📏 Total road length: {sum(edge.getLength() for edge in edges):.0f} meters")
            
            if edge_count > 10:
                print("✅ Network validation passed - ready for simulation!")
                return True
            else:
                print("⚠️ Network seems too small, might not be usable")
                return False
                
        except ImportError:
            print("⚠️ SUMO Python tools not available for detailed validation")
            print("💡 But network file was created successfully")
            return True
        except Exception as e:
            print(f"❌ Network validation failed: {e}")
            return False

def list_west_bengal_cities():
    """List all West Bengal cities with download status"""
    print("🏙️ West Bengal Cities Available for Download:")
    print("=" * 70)
    
    for city_name, city_data in WEST_BENGAL_CITIES.items():
        net_file = f"city_maps/real_cities/{city_name}.net.xml"
        osm_file = f"city_maps/real_cities/{city_name}.osm"
        
        if os.path.exists(net_file):
            status = "✅ READY"
        elif os.path.exists(osm_file):
            status = "🟡 OSM ONLY"
        else:
            status = "❌ NOT DOWNLOADED"
        
        print(f"  {status} {city_name:15} - {city_data['description']}")
    
    print(f"\n💡 Download command: python download_real_map.py <city_name>")

def list_west_bengal_regions():
    """List all West Bengal regions"""
    print("🗺️ West Bengal Regions Available:")
    print("=" * 50)
    
    for region_name, region_data in WEST_BENGAL_REGIONS.items():
        net_file = f"city_maps/real_cities/{region_name}.net.xml"
        status = "✅ READY" if os.path.exists(net_file) else "❌ NOT DOWNLOADED"
        
        print(f"  {status} {region_name:15} - {region_data['description']}")
    
    print(f"\n💡 Download command: python download_real_map.py --region <region_name>")

def download_west_bengal_region(region_name: str, downloader: OSMDownloader):
    """Download specific regions of West Bengal"""
    if region_name not in WEST_BENGAL_REGIONS:
        print(f"❌ Region '{region_name}' not found.")
        print(f"💡 Available regions: {list(WEST_BENGAL_REGIONS.keys())}")
        return None
    
    region_data = WEST_BENGAL_REGIONS[region_name]
    bbox = region_data["bbox"]
    description = region_data["description"]
    
    print(f"🗺️ Downloading {description}...")
    return downloader.download_city_by_bbox(region_name, bbox)

def check_sumo_installation():
    """Check if SUMO is properly installed"""
    try:
        result = os.system("netconvert --version > nul 2>&1")
        if result == 0:
            print("✅ SUMO netconvert tool is available")
            return True
        else:
            print("❌ SUMO netconvert tool not found in PATH")
            print("💡 Please install SUMO and add it to your system PATH")
            return False
    except:
        print("❌ Could not check SUMO installation")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Download real city maps for West Bengal cities - FIXED VERSION',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f'''
Examples:
  python download_real_map.py kolkata          # Download Kolkata
  python download_real_map.py durgapur --size 5.0  # Download with custom size
  python download_real_map.py --west-bengal    # List West Bengal cities
  python download_real_map.py --regions        # List West Bengal regions
  python download_real_map.py --region metro   # Download Kolkata metro area
  python download_real_map.py --bbox 22.55 88.33 22.58 88.38 --output kolkata_center

Popular Cities to Start With:
  kolkata    - Capital city, dense traffic
  durgapur   - Industrial city, good for testing
  saltlake   - Planned area, simpler network
  siliguri   - Strategic corridor, interesting routes
        '''
    )
    
    parser.add_argument('city', nargs='?', help='City name to download')
    parser.add_argument('--west-bengal', action='store_true', help='List West Bengal cities')
    parser.add_argument('--regions', action='store_true', help='List West Bengal regions')
    parser.add_argument('--region', type=str, help='Download West Bengal region (metro, industrial, siliguri)')
    parser.add_argument('--bbox', type=float, nargs=4, metavar=('MIN_LAT', 'MIN_LON', 'MAX_LAT', 'MAX_LON'),
                       help='Custom bounding box coordinates')
    parser.add_argument('--size', type=float, default=4.0, 
                       help='Area size in km (default: 4.0 km)')
    parser.add_argument('--no-convert', action='store_true', 
                       help='Download OSM only, don\'t convert to SUMO')
    parser.add_argument('--output', type=str, 
                       help='Custom output filename')
    parser.add_argument('--check-sumo', action='store_true',
                       help='Check SUMO installation')
    
    args = parser.parse_args()
    
    print("🗺️  Real Map Downloader - West Bengal Edition (FIXED)")
    print("=" * 55)
    print("📍 Specialized for West Bengal cities and regions")
    print("")
    
    # Check SUMO installation if requested
    if args.check_sumo:
        check_sumo_installation()
        return
    
    # Show lists if requested
    if args.west_bengal:
        list_west_bengal_cities()
        return
    
    if args.regions:
        list_west_bengal_regions()
        return
    
    # Download region if requested
    if args.region:
        downloader = OSMDownloader()
        osm_file = download_west_bengal_region(args.region, downloader)
        if osm_file and not args.no_convert:
            if check_sumo_installation():
                net_file = downloader.convert_osm_to_sumo(osm_file)
                if net_file:
                    downloader.validate_network(net_file)
                    print(f"🎉 Success! West Bengal region map ready: {net_file}")
            else:
                print("💡 OSM file downloaded, but SUMO conversion skipped")
        return
    
    # Check if city/bbox is provided
    if not args.city and not args.bbox:
        print("❌ Please specify a city name, region, or bounding box")
        print("💡 Use --west-bengal to see West Bengal cities")
        print("💡 Use --regions to see West Bengal regions")
        print("💡 Use --check-sumo to verify SUMO installation")
        print("\n📋 Quick Start Examples:")
        print("  python download_real_map.py kolkata")
        print("  python download_real_map.py --region metro") 
        print("  python download_real_map.py durgapur --size 5.0")
        return
    
    # Initialize downloader
    downloader = OSMDownloader()
    
    # Download based on bbox or city name
    if args.bbox:
        # Use custom bounding box
        city_name = args.output or f"custom_{args.bbox[0]:.4f}_{args.bbox[1]:.4f}"
        print(f"📐 Custom area: {args.bbox}")
        osm_file = downloader.download_city_by_bbox(city_name, tuple(args.bbox))
    else:
        # Use city name
        osm_file = downloader.download_city_by_name(args.city, args.size)
    
    if not osm_file:
        print("❌ Failed to download map data")
        sys.exit(1)
    
    # Convert to SUMO format if requested
    if not args.no_convert:
        if check_sumo_installation():
            net_file = downloader.convert_osm_to_sumo(osm_file)
            if net_file and downloader.validate_network(net_file):
                print(f"🎉 Success! Your city map is ready for AI training!")
                print(f"💡 Use this map: --city {args.city if args.city else city_name}")
                print(f"📁 Map location: {net_file}")
                
                # Show next steps
                print("\n🚀 Next Steps:")
                print("  1. Train AI assistant: python assistant.py --city " + 
                      f"{args.city if args.city else city_name} --days 100")
                print("  2. Compare cities: python analyze_west_bengal.py")
            else:
                print("❌ Failed to create usable SUMO network")
                sys.exit(1)
        else:
            print("💡 OSM file downloaded, but SUMO conversion skipped due to missing SUMO")
    else:
        print(f"🎉 OSM file downloaded: {osm_file}")
        print("💡 Convert later with: netconvert --osm-files " + 
              f'"{osm_file}" --output-file "{osm_file.replace(".osm", ".net.xml")}"')

if __name__ == "__main__":
    main()