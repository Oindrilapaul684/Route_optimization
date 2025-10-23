#!/usr/bin/env python3
"""
Analyze West Bengal city networks for route optimization
"""

import os
import sumolib
import matplotlib.pyplot as plt
import numpy as np
from settings.assistant_config import get_west_bengal_presets

def analyze_city_network(net_file: str):
    """Analyze a city network and return statistics"""
    if not os.path.exists(net_file):
        return None
    
    try:
        net = sumolib.net.readNet(net_file)
        
        edges = [edge for edge in net.getEdges() if edge.getFunction() == '']
        junctions = net.getNodes()
        
        stats = {
            'road_count': len(edges),
            'junction_count': len(junctions),
            'total_road_length': sum(edge.getLength() for edge in edges),
            'avg_road_length': np.mean([edge.getLength() for edge in edges]),
            'lanes_count': sum(edge.getLaneNumber() for edge in edges),
            'complexity_score': len(edges) * len(junctions) / 1000
        }
        
        return stats
    except Exception as e:
        print(f"❌ Error analyzing {net_file}: {e}")
        return None

def compare_west_bengal_cities():
    """Compare different West Bengal cities"""
    presets = get_west_bengal_presets()
    
    print("📊 West Bengal Cities Network Analysis")
    print("=" * 50)
    
    results = {}
    
    for city_name, config in presets.items():
        net_file = config['map_file']
        
        if os.path.exists(net_file):
            stats = analyze_city_network(net_file)
            if stats:
                results[city_name] = stats
                print(f"\n🏙️ {city_name.upper():20} - {config['description']}")
                print(f"   🛣️  Roads: {stats['road_count']:4d}")
                print(f"   🚦 Junctions: {stats['junction_count']:3d}")
                print(f"   📏 Total Length: {stats['total_road_length']:.0f}m")
                print(f"   📐 Avg Road: {stats['avg_road_length']:.1f}m")
                print(f"   🚗 Lanes: {stats['lanes_count']:3d}")
                print(f"   🧠 Complexity: {stats['complexity_score']:.2f}")
        else:
            print(f"❌ {city_name}: Map file not found - download with: python download_real_map.py {city_name}")
    
    # Create comparison chart
    if results:
        cities = list(results.keys())
        complexities = [results[city]['complexity_score'] for city in cities]
        road_counts = [results[city]['road_count'] for city in cities]
        
        plt.figure(figsize=(12, 6))
        
        plt.subplot(1, 2, 1)
        bars = plt.bar(cities, complexities, color='skyblue', edgecolor='navy')
        plt.title('Network Complexity of West Bengal Cities')
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('Complexity Score')
        
        # Add value labels on bars
        for bar, value in zip(bars, complexities):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                    f'{value:.1f}', ha='center', va='bottom')
        
        plt.subplot(1, 2, 2)
        bars = plt.bar(cities, road_counts, color='lightcoral', edgecolor='darkred')
        plt.title('Number of Roads in West Bengal Cities')
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('Road Count')
        
        # Add value labels on bars
        for bar, value in zip(bars, road_counts):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5, 
                    f'{value}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        os.makedirs('results', exist_ok=True)
        plt.savefig('results/west_bengal_cities_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"\n💡 Comparison chart saved: results/west_bengal_cities_comparison.png")

if __name__ == "__main__":
    compare_west_bengal_cities()