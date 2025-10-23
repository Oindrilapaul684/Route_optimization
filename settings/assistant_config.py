class AssistantPersonality:
    LEARNING_STYLE = {
        'curiosity_level': 0.1,
        'memory_strength': 0.95,
        'patience': 0.995,
        'min_curiosity': 0.01
    }
    
    DEEP_THINKER = {
        'learning_speed': 0.001,
        'memory_capacity': 10000,
        'focus_groups': 32,
        'wisdom_updates': 100,
        'epsilon': 1.0,
        'epsilon_min': 0.01,
        'epsilon_decay': 0.995,
        'discount_factor': 0.95
    }
    
    CITY = {
        'map_file': 'city_maps/real_cities/kolkata.net.xml',
        'show_visuals': True,
        'number_of_cars': 50,
        'simulation_time': 3600,
        'time_step': 1.0
    }

# Enhanced configuration with West Bengal cities
REAL_CITY_PRESETS = {
    # West Bengal Cities
    'kolkata': {
        'map_file': 'city_maps/real_cities/kolkata.net.xml',
        'recommended_vehicles': 60,
        'complexity': 'very high',
        'description': 'Capital City - Dense Urban Traffic'
    },
    'durgapur': {
        'map_file': 'city_maps/real_cities/durgapur.net.xml',
        'recommended_vehicles': 35,
        'complexity': 'medium',
        'description': 'Industrial City - Mixed Traffic'
    },
    'asansol': {
        'map_file': 'city_maps/real_cities/asansol.net.xml', 
        'recommended_vehicles': 40,
        'complexity': 'medium',
        'description': 'Mining City - Heavy Vehicle Traffic'
    },
    'siliguri': {
        'map_file': 'city_maps/real_cities/siliguri.net.xml',
        'recommended_vehicles': 45,
        'complexity': 'high',
        'description': 'Gateway to Northeast - Strategic Corridor'
    },
    'howrah': {
        'map_file': 'city_maps/real_cities/howrah.net.xml',
        'recommended_vehicles': 55,
        'complexity': 'high', 
        'description': 'Twin City of Kolkata - Bridge Traffic'
    },
    'kharagpur': {
        'map_file': 'city_maps/real_cities/kharagpur.net.xml',
        'recommended_vehicles': 30,
        'complexity': 'medium',
        'description': 'Railway Town - Educational Hub'
    },
    'saltlake': {
        'map_file': 'city_maps/real_cities/saltlake.net.xml',
        'recommended_vehicles': 25,
        'complexity': 'low',
        'description': 'Planned Township - Grid Layout'
    },
    'newtown': {
        'map_file': 'city_maps/real_cities/newtown.net.xml',
        'recommended_vehicles': 20,
        'complexity': 'low',
        'description': 'IT Hub - Modern Infrastructure'
    },
    
    # Regions
    'kolkata_metro': {
        'map_file': 'city_maps/real_cities/kolkata_metro.net.xml',
        'recommended_vehicles': 80,
        'complexity': 'very high',
        'description': 'Metropolitan Area - Complex Network'
    },
    'industrial_corridor': {
        'map_file': 'city_maps/real_cities/industrial_corridor.net.xml', 
        'recommended_vehicles': 50,
        'complexity': 'high',
        'description': 'Durgapur-Asansol Belt - Industrial Traffic'
    },
    
    # Default fallback
    'default': {
        'map_file': 'city_maps/downtown.net.xml',
        'recommended_vehicles': 30,
        'complexity': 'low',
        'description': 'Simple Grid Network'
    }
}

def get_west_bengal_presets():
    """Get only West Bengal city presets"""
    return {k: v for k, v in REAL_CITY_PRESETS.items() 
            if k in ['kolkata', 'durgapur', 'asansol', 'siliguri', 'howrah', 
                    'kharagpur', 'saltlake', 'newtown', 'kolkata_metro', 'industrial_corridor']}