import numpy as np
import pickle
import os
from typing import Dict

class QuickLearner:
    def __init__(self, observation_size: int, decision_options: int, personality: dict):
        self.observation_size = observation_size
        self.decision_options = decision_options
        self.personality = personality
        
        # Experience notebook
        self.experience_book = {}
        
        # Learning style
        self.curiosity = personality['curiosity_level']
        self.memory_power = personality['memory_strength']
        self.patience = personality['patience']
        self.min_curiosity = personality['min_curiosity']
        
        # Learning diary
        self.learning_diary = []
    
    def make_decision(self, situation: np.ndarray) -> int:
        """Make a decision based on current situation"""
        situation_code = self._situation_to_code(situation)
        
        # First time seeing this situation? Initialize options
        if situation_code not in self.experience_book:
            self.experience_book[situation_code] = np.zeros(self.decision_options)
        
        # Explore or use experience?
        if np.random.random() < self.curiosity:
            return np.random.randint(self.decision_options)  # Try something new!
        else:
            return np.argmax(self.experience_book[situation_code])  # Use best known option
    
    def learn_from_experience(self, situation: np.ndarray, decision: int, 
                            outcome: float, next_situation: np.ndarray, done: bool):
        """Learn from what just happened"""
        situation_code = self._situation_to_code(situation)
        next_situation_code = self._situation_to_code(next_situation)
        
        # Record new situations
        if situation_code not in self.experience_book:
            self.experience_book[situation_code] = np.zeros(self.decision_options)
        if next_situation_code not in self.experience_book:
            self.experience_book[next_situation_code] = np.zeros(self.decision_options)
        
        # Learn from this experience
        current_knowledge = self.experience_book[situation_code][decision]
        
        if done:
            learned_value = outcome
        else:
            learned_value = outcome + self.memory_power * np.max(self.experience_book[next_situation_code])
        
        # Update knowledge
        self.experience_book[situation_code][decision] = current_knowledge + self.curiosity * (learned_value - current_knowledge)
        
        # Become slightly less curious over time (but never stop completely)
        if done:
            self.curiosity = max(
                self.min_curiosity, 
                self.curiosity * self.patience
            )
    
    def _situation_to_code(self, situation: np.ndarray) -> str:
        """Convert situation to simple code"""
        simplified_situation = (situation * 10).astype(int)
        return ','.join(map(str, simplified_situation))
    
    def save_knowledge(self, filepath: str):
        """Save all learned knowledge"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump({
                'experience_book': self.experience_book,
                'current_curiosity': self.curiosity,
                'learning_diary': self.learning_diary
            }, f)
        print(f"💾 Knowledge saved: {filepath}")
    
    def load_knowledge(self, filepath: str):
        """Load previously learned knowledge"""
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                saved_knowledge = pickle.load(f)
                self.experience_book = saved_knowledge['experience_book']
                self.curiosity = saved_knowledge['current_curiosity']
                self.learning_diary = saved_knowledge['learning_diary']
            print(f"📖 Knowledge loaded: {filepath}")
    
    def record_journey(self, day: int, total_outcome: float, steps: int):
        """Record today's learning progress"""
        self.learning_diary.append({
            'day': day,
            'total_outcome': total_outcome,
            'steps_taken': steps,
            'curiosity_level': self.curiosity
        })