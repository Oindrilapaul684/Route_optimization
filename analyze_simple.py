#!/usr/bin/env python3
"""
Simple Analysis of Downloaded Cities
"""

import os
import matplotlib.pyplot as plt

def analyze_downloaded_cities():
    """Analyze what cities we have downloaded"""
    cities_dir = "city_maps/real_cities"
    
    if not os.path.exists(cities_dir):
        print("❌ No cities downloaded yet")
        return
    
    cities = {}
    for file in os.listdir(cities_dir):
        if file.endswith('.net.xml'):
            city_name = file.replace('.net.xml', '')
            file_path = os.path.join(cities_dir, file)
            file_size_kb = os.path.getsize(file_path) / 1024
            cities[city_name] = file_size_kb
    
    if not cities:
        print("❌ No SUMO network files found")
        return
    
    print("📊 Downloaded Cities Analysis")
    print("=" * 40)
    
    for city, size in cities.items():
        print(f"🏙️ {city:15} - {size:6.1f} KB")
    
    # Create visualization
    if len(cities) > 1:
        plt.figure(figsize=(10, 6))
        
        names = list(cities.keys())
        sizes = list(cities.values())
        
        plt.bar(names, sizes, color=['skyblue', 'lightcoral', 'lightgreen'])
        plt.title('Downloaded City Network Sizes')
        plt.ylabel('File Size (KB)')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for i, v in enumerate(sizes):
            plt.text(i, v + 0.5, f'{v:.1f} KB', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig('results/city_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"\n📈 Analysis chart saved: results/city_analysis.png")

def main():
    print("🔍 Simple City Analysis")
    print("=" * 25)
    analyze_downloaded_cities()

if __name__ == "__main__":
    main()