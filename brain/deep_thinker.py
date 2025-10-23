import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np
import random
from collections import deque
import os

class DeepThinker:
    def __init__(self, observation_size: int, decision_options: int, personality: dict):
        self.state_size = observation_size
        self.action_size = decision_options
        self.personality = personality
        
        # Neural network brain
        self.model = self._build_model()
        self.target_model = self._build_model()
        self.update_target_network()
        
        # Memory storage
        self.memory = deque(maxlen=personality['memory_capacity'])
        
        # Learning parameters
        self.epsilon = personality.get('epsilon', 1.0)
        self.epsilon_min = personality.get('epsilon_min', 0.01)
        self.epsilon_decay = personality.get('epsilon_decay', 0.995)
        self.learning_rate = personality.get('learning_speed', 0.001)
        self.batch_size = personality.get('focus_groups', 32)
        self.discount_factor = personality.get('discount_factor', 0.95)
        
        # Training history
        self.training_history = []
    
    def _build_model(self):
        """Build the neural network"""
        model = models.Sequential([
            layers.Dense(64, activation='relu', input_shape=(self.state_size,)),
            layers.Dense(64, activation='relu'),
            layers.Dense(64, activation='relu'),
            layers.Dense(self.action_size, activation='linear')
        ])
        
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=self.learning_rate),
            loss='mse'
        )
        
        return model
    
    def update_target_network(self):
        """Update target network weights"""
        self.target_model.set_weights(self.model.get_weights())
    
    def get_action(self, state):
        """Get action using epsilon-greedy policy"""
        if np.random.random() <= self.epsilon:
            return random.randrange(self.action_size)
        
        state = state.reshape(1, -1)
        q_values = self.model.predict(state, verbose=0)
        return np.argmax(q_values[0])
    
    def remember(self, state, action, reward, next_state, done):
        """Store experience in replay memory"""
        self.memory.append((state, action, reward, next_state, done))
    
    def replay(self):
        """Train model on random batch from replay memory"""
        if len(self.memory) < self.batch_size:
            return
        
        batch = random.sample(self.memory, self.batch_size)
        states = np.array([experience[0] for experience in batch])
        actions = np.array([experience[1] for experience in batch])
        rewards = np.array([experience[2] for experience in batch])
        next_states = np.array([experience[3] for experience in batch])
        dones = np.array([experience[4] for experience in batch])
        
        # Current Q-values
        current_q = self.model.predict(states, verbose=0)
        
        # Target Q-values
        target_q = self.model.predict(states, verbose=0)
        next_q = self.target_model.predict(next_states, verbose=0)
        
        for i in range(self.batch_size):
            if dones[i]:
                target_q[i][actions[i]] = rewards[i]
            else:
                target_q[i][actions[i]] = rewards[i] + self.discount_factor * np.max(next_q[i])
        
        # Train model
        self.model.fit(states, target_q, epochs=1, verbose=0, batch_size=self.batch_size)
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def save_model(self, filepath):
        """Save model weights"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        self.model.save_weights(filepath + '.h5')
        
        # Save training history
        import pickle
        with open(filepath + '_history.pkl', 'wb') as f:
            pickle.dump(self.training_history, f)
        
        print(f"💾 Deep Thinker model saved: {filepath}")
    
    def load_model(self, filepath):
        """Load model weights"""
        if os.path.exists(filepath + '.h5'):
            self.model.load_weights(filepath + '.h5')
            self.update_target_network()
            
            # Load training history
            import pickle
            if os.path.exists(filepath + '_history.pkl'):
                with open(filepath + '_history.pkl', 'rb') as f:
                    self.training_history = pickle.load(f)
            
            print(f"📖 Deep Thinker model loaded: {filepath}")
    
    def record_episode(self, episode, total_reward, steps):
        """Record episode statistics"""
        self.training_history.append({
            'episode': episode,
            'total_reward': total_reward,
            'steps': steps,
            'epsilon': self.epsilon
        })