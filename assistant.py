#!/usr/bin/env python3
"""
Smart Route Assistant - West Bengal Edition
AI-powered route optimization for West Bengal cities
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
from settings.assistant_config import AssistantPersonality, REAL_CITY_PRESETS, get_west_bengal_presets
from brain.navigation_mind import CityNavigator
from brain.quick_learner import QuickLearner
from brain.deep_thinker import DeepThinker
import os
import sys

def check_sumo_installation():
    """Check if SUMO is properly installed"""
    try:
        import traci
        import sumolib
        print("✅ SUMO Python libraries found")
        return True
    except ImportError as e:
        print(f"❌ SUMO Python libraries not found: {e}")
        print("\n💡 Please install SUMO and ensure it's in your Python path")
        print("   Windows: Download from https://github.com/eclipse/sumo/releases")
        print("   macOS: brew install sumo")
        print("   Linux: sudo apt-get install sumo sumo-tools")
        return False

def setup_city_environment(city_name="default"):
    """Setup the city environment with support for real cities"""
    print("🏙️ Setting up city environment...")
    
    # Get city configuration
    city_config = REAL_CITY_PRESETS.get(city_name, REAL_CITY_PRESETS['default'])
    net_file = city_config['map_file']
    
    # Check if the map file exists
    if not os.path.exists(net_file):
        print(f"❌ City map not found: {net_file}")
        
        if city_name != "default":
            print(f"💡 Download {city_name} map first: python download_real_map.py {city_name}")
            # Fall back to default
            city_config = REAL_CITY_PRESETS['default']
            net_file = city_config['map_file']
            
            # Create default if it doesn't exist
            if not os.path.exists(net_file):
                print("📝 Creating default city network...")
                os.system("netgenerate --grid --grid.number=6 --grid.length=150 --output-file=city_maps/downtown.net.xml")
    
    config = {
        'map_file': net_file,
        'show_visuals': True,
        'number_of_cars': city_config['recommended_vehicles'],
        'simulation_time': 3600,
        'time_step': 1.0
    }
    
    print(f"📍 Using city: {city_name} ({city_config['complexity']} complexity)")
    print(f"🚗 Vehicles: {city_config['recommended_vehicles']}")
    print(f"📋 Description: {city_config['description']}")
    
    return net_file, config

def train_quick_learner(net_file, config, learning_days=100):
    """Train the quick learning assistant"""
    print("\n🧠 Training Quick Learner Assistant...")
    
    city = CityNavigator(net_file, config)
    
    assistant = QuickLearner(
        observation_size=city.attention_spots,
        decision_options=4,
        personality=AssistantPersonality.LEARNING_STYLE
    )
    
    print(f"🎯 Starting training for {learning_days} days in {os.path.basename(net_file)}...")
    
    for day in range(learning_days):
        situation = city.start_new_day()
        total_reward = 0
        steps = 0
        
        while True:
            action = assistant.make_decision(situation)
            next_situation, reward, done, info = city.make_move(action)
            
            assistant.learn_from_experience(situation, action, reward, next_situation, done)
            
            situation = next_situation
            total_reward += reward
            steps += 1
            
            if done:
                break
        
        assistant.record_journey(day, total_reward, steps)
        
        if day % 10 == 0:
            print(f"📅 Day {day:3d} | Reward: {total_reward:7.2f} | Steps: {steps:3d} | Curiosity: {assistant.curiosity:.3f}")
    
    # Save results
    city_name = os.path.basename(net_file).replace('.net.xml', '')
    os.makedirs("memories", exist_ok=True)
    assistant.save_knowledge(f"memories/quick_learner_{city_name}.pkl")
    
    city.end_day()
    return assistant

def train_deep_thinker(net_file, config, learning_days=100):
    """Train deep thinker with SUMO integration"""
    print("\n🧠 Training Deep Thinker Assistant...")
    
    city = CityNavigator(net_file, config)
    thinker = DeepThinker(
        observation_size=city.attention_spots,
        decision_options=4,
        personality=AssistantPersonality.DEEP_THINKER
    )
    
    for day in range(learning_days):
        situation = city.start_new_day()
        total_reward = 0
        steps = 0
        
        while True:
            action = thinker.get_action(situation)
            next_situation, reward, done, info = city.make_move(action)
            
            thinker.remember(situation, action, reward, next_situation, done)
            thinker.replay()
            
            situation = next_situation
            total_reward += reward
            steps += 1
            
            if done:
                break
        
        # Update target network periodically
        if day % AssistantPersonality.DEEP_THINKER['wisdom_updates'] == 0:
            thinker.update_target_network()
        
        thinker.record_episode(day, total_reward, steps)
        
        if day % 10 == 0:
            print(f"📅 Day {day:3d} | Reward: {total_reward:7.2f} | Steps: {steps:3d} | Epsilon: {thinker.epsilon:.3f}")
    
    # Save model
    city_name = os.path.basename(net_file).replace('.net.xml', '')
    thinker.save_model(f"memories/deep_thinker_{city_name}")
    
    city.end_day()
    return thinker

def show_learning_progress(assistant, assistant_name: str):
    """Show learning progress"""
    if hasattr(assistant, 'learning_diary') and assistant.learning_diary:
        journal = assistant.learning_diary
    elif hasattr(assistant, 'training_history') and assistant.training_history:
        journal = assistant.training_history
    else:
        print("No learning data to display")
        return
    
    days = [entry['day'] for entry in journal]
    rewards = [entry['total_reward'] for entry in journal]
    
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(days, rewards, 'b-', alpha=0.7)
    plt.title(f'{assistant_name} - Learning Progress')
    plt.xlabel('Training Days')
    plt.ylabel('Total Reward')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 2, 2)
    if 'curiosity_level' in journal[0]:
        curiosity = [entry['curiosity_level'] for entry in journal]
        plt.plot(days, curiosity, 'r-', label='Curiosity Level', alpha=0.7)
    elif 'epsilon' in journal[0]:
        epsilon = [entry['epsilon'] for entry in journal]
        plt.plot(days, epsilon, 'r-', label='Epsilon', alpha=0.7)
    
    plt.title(f'{assistant_name} - Exploration Rate')
    plt.xlabel('Training Days')
    plt.ylabel('Rate')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save plot
    os.makedirs("results", exist_ok=True)
    filename = f"results/{assistant_name.lower().replace(' ', '_')}_progress.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"📊 Progress chart saved: {filename}")

def main():
    print("🚗 Welcome to Smart Route Assistant - West Bengal Edition! 🧠")
    print("=" * 60)
    
    # Check SUMO installation
    if not check_sumo_installation():
        return
    
    parser = argparse.ArgumentParser(description='Smart Route Assistant for West Bengal Cities')
    parser.add_argument('--city', type=str, default='kolkata', 
                       help='City name (kolkata, durgapur, asansol, etc. Use "list" to see all)')
    parser.add_argument('--days', type=int, default=100, help='Number of training days')
    parser.add_argument('--no-gui', action='store_true', help='Run without SUMO GUI')
    parser.add_argument('--list-cities', action='store_true', help='List available city presets')
    parser.add_argument('--assistant', type=str, choices=['quick', 'thinker', 'both'], 
                       default='quick', help='Which assistant to train')
    
    args = parser.parse_args()
    
    if args.list_cities:
        print("🏙️ Available City Presets:")
        wb_presets = get_west_bengal_presets()
        for city_name, config in wb_presets.items():
            exists = "✅" if os.path.exists(config['map_file']) else "❌"
            print(f"  {exists} {city_name:20} - {config['complexity']:8} - {config['description']}")
        print("\n💡 Download cities with: python download_real_map.py <city_name>")
        return
    
    try:
        # Setup environment with specified city
        net_file, config = setup_city_environment(args.city)
        
        if args.no_gui:
            config['show_visuals'] = False
        
        # Train the assistant(s)
        assistants = []
        
        if args.assistant in ['quick', 'both']:
            quick_assistant = train_quick_learner(net_file, config, args.days)
            assistants.append(('Quick Learner', quick_assistant))
        
        if args.assistant in ['thinker', 'both']:
            thinker_assistant = train_deep_thinker(net_file, config, args.days)
            assistants.append(('Deep Thinker', thinker_assistant))
        
        # Show results
        for assistant_name, assistant in assistants:
            show_learning_progress(assistant, f"{assistant_name} - {args.city}")
        
        print("\n🎉 Training completed successfully!")
        print(f"📊 Results saved in 'results' folder")
        print(f"💾 Models saved in 'memories' folder")
        
    except Exception as e:
        print(f"❌ Error during training: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()