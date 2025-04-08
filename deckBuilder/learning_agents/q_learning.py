import random
import numpy as np
from ..DeckBuilder import DeckBuilderEnv

class QLearningAgent:
    def __init__(self, env, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.env = env
        self.alpha = alpha  # learning rate
        self.gamma = gamma  # discount rate
        self.epsilon = epsilon  # exploration rate
        self.q_table = {}  
        self.reset()

    def reset(self):
        self.state = self.env.reset()  

    def choose_action(self):
        state_tuple = tuple(self.state.flatten())  
        
        if state_tuple not in self.q_table:
            self.q_table[state_tuple] = np.zeros(self.env.action_space.n)

        if np.random.uniform(0, 1) < self.epsilon:
            return self.env.action_space.sample()
        else:
            return np.argmax(self.q_table[state_tuple])

    def learn(self, action, reward, next_state):
        state_tuple = tuple(self.state.flatten())
        next_state_tuple = tuple(next_state.flatten())

        if next_state_tuple not in self.q_table:
            self.q_table[next_state_tuple] = np.zeros(self.env.action_space.n)

        best_future_q = np.max(self.q_table[next_state_tuple])  
        current_q = self.q_table[state_tuple][action] 
        
        # Q-learning formula
        self.q_table[state_tuple][action] = current_q + self.alpha * (reward + self.gamma * best_future_q - current_q)

    def train(self, episodes=1000):
        for episode in range(episodes):
            self.reset()
            done = False
            total_reward = 0
            
            while not done:
                action = self.choose_action()
                next_state, reward, done, _ = self.env.step(action)
                
                self.learn(action, reward, next_state)
                
                self.state = next_state
                total_reward += reward

            print(f"Episode {episode+1}/{episodes}: Total Reward: {total_reward}")
