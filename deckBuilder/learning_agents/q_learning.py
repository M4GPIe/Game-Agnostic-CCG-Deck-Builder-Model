import random
import numpy as np
from ..DeckBuilder import DeckBuilderEnv

class QLearningAgent:
    def __init__(self, env, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.env = env
        self.alpha = alpha  # Tasa de aprendizaje
        self.gamma = gamma  # Factor de descuento
        self.epsilon = epsilon  # Tasa de exploración
        self.q_table = {}  # Tabla Q
        self.reset()

    def reset(self):
        self.state = self.env.reset()  # Resetea el entorno y obtiene el estado inicial

    def choose_action(self):
        # Convertir el estado a una tupla para usarlo como clave en la tabla Q
        state_tuple = tuple(self.state.flatten())  # Convierte el estado (un ndarray) a tupla
        
        # Si el estado no está en la tabla Q, inicializamos con valores cero
        if state_tuple not in self.q_table:
            self.q_table[state_tuple] = np.zeros(self.env.action_space.n)

        # Exploración vs Explotación
        if np.random.uniform(0, 1) < self.epsilon:
            # Exploración: seleccionar una acción aleatoria
            return self.env.action_space.sample()
        else:
            # Explotación: seleccionar la acción con el valor máximo de Q
            return np.argmax(self.q_table[state_tuple])

    def learn(self, action, reward, next_state):
        # Convertir el estado y el siguiente estado a tuplas
        state_tuple = tuple(self.state.flatten())
        next_state_tuple = tuple(next_state.flatten())

        # Si no existe el siguiente estado en la tabla Q, inicializamos con valores cero
        if next_state_tuple not in self.q_table:
            self.q_table[next_state_tuple] = np.zeros(self.env.action_space.n)

        # Actualizamos el valor de Q para el estado y la acción actual
        best_future_q = np.max(self.q_table[next_state_tuple])  # El máximo Q del siguiente estado
        current_q = self.q_table[state_tuple][action]  # El Q actual para el par estado-acción
        
        # Aplicamos la fórmula de Q-learning
        self.q_table[state_tuple][action] = current_q + self.alpha * (reward + self.gamma * best_future_q - current_q)

    def train(self, episodes=1000):
        for episode in range(episodes):
            self.reset()
            done = False
            total_reward = 0
            
            while not done:
                action = self.choose_action()
                next_state, reward, done, _ = self.env.step(action)
                
                # Aprende del paso
                self.learn(action, reward, next_state)
                
                # Actualiza el estado actual
                self.state = next_state
                total_reward += reward

            print(f"Episode {episode+1}/{episodes}: Total Reward: {total_reward}")
