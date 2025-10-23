import traci
import sumolib
import numpy as np
from typing import List, Tuple, Dict
import os

class CityNavigator:
    def __init__(self, city_map: str, personality: dict):
        self.city_map = city_map
        self.personality = personality
        
        try:
            self.city_layout = sumolib.net.readNet(city_map)
            print(f"✅ Loaded city network: {os.path.basename(city_map)}")
        except Exception as e:
            print(f"⚠️ Could not load city map {city_map}: {e}")
            print("📝 Creating emergency grid network...")
            self._create_emergency_map()
            self.city_layout = sumolib.net.readNet('city_maps/downtown.net.xml')
        
        self.attention_spots = 10
        self.current_car = None
        self.time_elapsed = 0
        self.max_journey_time = 500
    
    def _create_emergency_map(self):
        """Create a simple map if none exists"""
        os.makedirs('city_maps', exist_ok=True)
        os.system("netgenerate --grid --grid.number=4 --grid.length=200 --output-file=city_maps/downtown.net.xml")
    
    def start_new_day(self):
        """Start simulation"""
        try:
            if traci.isLoaded():
                traci.close()
            
            sumo_cmd = [
                'sumo-gui' if self.personality['show_visuals'] else 'sumo',
                '-n', self.city_map,
                '--waiting-time-memory', '1000',
                '--random'
            ]
            
            traci.start(sumo_cmd)
            self.all_cars = traci.vehicle.getIDList()
            self.current_car = self.all_cars[0] if self.all_cars else None
            self.time_elapsed = 0
            
            print(f"🚗 Simulation started with {len(self.all_cars)} vehicles")
            return self._look_around()
            
        except Exception as e:
            print(f"❌ Error starting simulation: {e}")
            return np.zeros(self.attention_spots, dtype=np.float32)
    
    def make_move(self, decision: int) -> Tuple[np.ndarray, float, bool, dict]:
        """Make a move in the simulation"""
        self.time_elapsed += 1
        
        # Apply routing decision
        self._take_route(decision)
        
        # Advance simulation
        traci.simulationStep()
        
        # Get results
        observation = self._look_around()
        reward = self._calculate_satisfaction()
        done = self._is_journey_over()
        
        info = {
            'car_id': self.current_car,
            'time_elapsed': self.time_elapsed,
            'total_travel_time': self._get_travel_time()
        }
        
        return observation, reward, done, info
    
    def _look_around(self) -> np.ndarray:
        """What our assistant notices about current situation"""
        if not self.current_car:
            return np.zeros(self.attention_spots, dtype=np.float32)
        
        observations = []
        
        try:
            # Check current road congestion
            current_road = traci.vehicle.getRoadID(self.current_car)
            cars_on_road = traci.edge.getLastStepVehicleNumber(current_road)
            road_length = traci.lane.getLength(current_road + '_0')
            observations.append(cars_on_road / road_length if road_length > 0 else 0)
            
            # Check nearby roads
            nearby_roads = self._find_nearby_roads(current_road)
            for road in nearby_roads[:4]:
                if road:
                    density = traci.edge.getLastStepVehicleNumber(road) / traci.lane.getLength(road + '_0')
                    observations.append(min(density, 1.0))
                else:
                    observations.append(0.0)
            
            # Current speed and waiting time
            observations.append(traci.vehicle.getSpeed(self.current_car) / 13.89)  # Normalized
            observations.append(traci.vehicle.getWaitingTime(self.current_car) / 100.0)
            
            # How long we've been driving
            observations.append(self.time_elapsed / self.max_journey_time)
            
        except Exception as e:
            print(f"⚠️ Error in observation: {e}")
        
        # Fill remaining spots
        while len(observations) < self.attention_spots:
            observations.append(0.0)
        
        return np.array(observations[:self.attention_spots], dtype=np.float32)
    
    def _take_route(self, route_choice: int):
        """Choose which way to go"""
        if not self.current_car:
            return
        
        try:
            current_road = traci.vehicle.getRoadID(self.current_car)
            possible_paths = self._find_possible_paths(current_road)
            
            if route_choice < len(possible_paths):
                chosen_path = possible_paths[route_choice]
                self._adjust_route(chosen_path)
        except Exception as e:
            print(f"⚠️ Error in route decision: {e}")
    
    def _calculate_satisfaction(self) -> float:
        """How happy our assistant is with current progress"""
        if not self.current_car:
            return 0.0
        
        happiness = 0.1  # Small reward for moving
        
        try:
            # Don't like waiting in traffic
            waiting_time = traci.vehicle.getWaitingTime(self.current_car)
            happiness -= waiting_time * 0.01
            
            # Love moving at good speed
            current_speed = traci.vehicle.getSpeed(self.current_car)
            max_speed = traci.vehicle.getMaxSpeed(self.current_car)
            if max_speed > 0:
                speed_ratio = current_speed / max_speed
                happiness += speed_ratio * 0.1
            
            # Really dislike being stuck
            if current_speed == 0 and waiting_time > 30:
                happiness -= 0.5
                
        except Exception as e:
            print(f"⚠️ Error calculating reward: {e}")
        
        return happiness
    
    def _is_journey_over(self) -> bool:
        """Check if we've reached destination or time's up"""
        if not self.current_car:
            return True
        
        try:
            arrived = traci.simulation.getArrivedNumber() > 0
            took_too_long = self.time_elapsed >= self.max_journey_time
            return arrived or took_too_long
        except:
            return self.time_elapsed >= self.max_journey_time
    
    def _find_nearby_roads(self, current_road: str) -> List[str]:
        """Find roads connected to current position"""
        nearby = []
        try:
            road_obj = self.city_layout.getEdge(current_road)
            
            # Roads ahead
            for next_road in road_obj.getOutgoing():
                nearby.append(next_road.getID())
            
            # Roads behind
            for prev_road in road_obj.getIncoming():
                nearby.append(prev_road.getID())
                
        except:
            pass
        
        return nearby[:8]
    
    def _find_possible_paths(self, current_road: str) -> List[str]:
        """Find all possible next roads from current position"""
        try:
            road_obj = self.city_layout.getEdge(current_road)
            return [road.getID() for road in road_obj.getOutgoing()]
        except:
            return []
    
    def _adjust_route(self, target_road: str):
        """Change route to prefer the chosen road"""
        try:
            current_route = traci.vehicle.getRoute(self.current_car)
            current_position = current_route.index(traci.vehicle.getRoadID(self.current_car))
            
            remaining_route = current_route[current_position:]
            if target_road in remaining_route:
                new_route = [current_route[current_position]]
                new_route.extend([road for road in remaining_route if road != target_road])
                new_route.append(target_road)
                
                traci.vehicle.setRoute(self.current_car, new_route)
        except:
            pass
    
    def _get_travel_time(self) -> float:
        """Get current travel time"""
        return float(self.time_elapsed)
    
    def end_day(self):
        """Close simulation"""
        try:
            if traci.isLoaded():
                traci.close()
                print("🛑 Simulation ended")
        except:
            pass