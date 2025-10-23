#!/usr/bin/env python3
"""
Simple Assistant for Testing - No SUMO required initially
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import pickle

class SimpleCity:
    """Simple simulated city environment"""
    def __init__(self, city_name):
        self.city_name = city_name
        self.steps = 0
        self.max_steps = 100
        
    def reset(self):
        """Reset simulation"""
        self.steps = 0
        print(f"🏙️ Starting simulation in {self.city_name}")
        return np.random.random(10)  # Fake observations
    
    def step(self, action):
        """Take a step in simulation"""
        self.steps += 1
        
        # Fake reward based on action
        reward = np.random.normal(1.0, 0.5)
        
        # Fake next state
        next_state = np.random.random(10)
        
        # Check if done
        done = self.steps >= self.max_steps or np.random.random() < 0.01
        
        info = {"steps": self.steps, "city": self.city_name}
        
        return next_state, reward, done, info

class SimpleQLearner:
    """Simple Q-learning agent"""
    def __init__(self):
        self.q_table = defaultdict(lambda: np.zeros(4))
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.1
        self.history = []
    
    def choose_action(self, state):
        """Choose action using epsilon-greedy"""
        state_key = tuple(np.round(state, 2))
        
        if np.random.random() < self.epsilon:
            return np.random.randint(4)  # Explore
        else:
            return np.argmax(self.q_table[state_key])  # Exploit
    
    def learn(self, state, action, reward, next_state, done):
        """Learn from experience"""
        state_key = tuple(np.round(state, 2))
        next_state_key = tuple(np.round(next_state, 2))
        
        # Q-learning update
        current_q = self.q_table[state_key][action]
        next_max_q = np.max(self.q_table[next_state_key])
        
        target_q = reward + 0.95 * next_max_q * (not done)
        self.q_table[state_key][action] = current_q + self.learning_rate * (target_q - current_q)
        
        # Decay epsilon
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
    
    def train(self, city_name, episodes=50):
        """Train the agent"""
        city = SimpleCity(city_name)
        
        print(f"🧠 Training Simple Q-Learner in {city_name}")
        print("=" * 50)
        
        for episode in range(episodes):
            state = city.reset()
            total_reward = 0
            
            while True:
                action = self.choose_action(state)
                next_state, reward, done, info = city.step(action)
                
                self.learn(state, action, reward, next_state, done)
                
                state = next_state
                total_reward += reward
                
                if done:
                    break
            
            self.history.append({
                'episode': episode,
                'total_reward': total_reward,
                'epsilon': self.epsilon,
                'steps': info['steps']
            })
            
            if episode % 10 == 0:
                print(f"📅 Episode {episode:3d} | Reward: {total_reward:7.2f} | " +
                      f"Steps: {info['steps']:3d} | Epsilon: {self.epsilon:.3f}")
        
        return self.history
    
    def plot_progress(self, city_name):
        """Plot training progress"""
        if not self.history:
            print("No training data to plot")
            return
        
        episodes = [h['episode'] for h in self.history]
        rewards = [h['total_reward'] for h in self.history]
        epsilons = [h['epsilon'] for h in self.history]
        
        plt.figure(figsize=(12, 4))
        
        plt.subplot(1, 2, 1)
        plt.plot(episodes, rewards, 'b-', alpha=0.7)
        plt.title(f'Training Progress - {city_name}')
        plt.xlabel('Episode')
        plt.ylabel('Total Reward')
        plt.grid(True, alpha=0.3)
        
        plt.subplot(1, 2, 2)
        plt.plot(episodes, epsilons, 'r-', alpha=0.7)
        plt.title('Exploration Rate')
        plt.xlabel('Episode')
        plt.ylabel('Epsilon')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save plot
        os.makedirs('results', exist_ok=True)
        filename = f'results/simple_training_{city_name}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"📊 Progress chart saved: {filename}")

def main():
    """Main function"""
    print("🧠 Simple Route Assistant - Testing Mode")
    print("=" * 40)
    
    # Check if we have any downloaded cities
    cities_dir = "city_maps/real_cities"
    if os.path.exists(cities_dir):
        cities = [f.replace('.net.xml', '') for f in os.listdir(cities_dir) 
                 if f.endswith('.net.xml')]
        if cities:
            print("✅ Found downloaded cities:", cities)
        else:
            print("ℹ️ No city maps found. Run download_real_map.py first")
            cities = ['simulated_city']
    else:
        cities = ['simulated_city']
    
    # Train on available cities
    for city in cities[:2]:  # Limit to 2 cities for demo
        print(f"\n🎯 Training on: {city}")
        
        agent = SimpleQLearner()
        history = agent.train(city, episodes=30)
        agent.plot_progress(city)
        
        # Save agent
        os.makedirs('memories', exist_ok=True)
        with open(f'memories/simple_agent_{city}.pkl', 'wb') as f:
            pickle.dump(agent.q_table, f)
        
        print(f"💾 Agent saved: memories/simple_agent_{city}.pkl")
    
    print(f"\n🎉 Simple training completed!")
    print("📁 Check 'results' folder for progress charts")
    print("📁 Check 'memories' folder for saved agents")

if __name__ == "__main__":
    main()