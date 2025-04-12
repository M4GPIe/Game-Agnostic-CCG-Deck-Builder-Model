from stable_baselines3 import PPO, DQN, A2C,DDPG
from stable_baselines3.common.vec_env import DummyVecEnv
import torch

# cambiar a stable baselines PPo2 TD3 DDPQ y DQN
# comparar diferentes algoritmos y resultados

class TrainAgent:
    def __init__(self, env):
        self.env = env
        
    def train(self, total_timesteps: int):
        
        vec_env = DummyVecEnv([lambda: self.env])
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        model = DQN("MlpPolicy", vec_env, verbose=0, device=device)
        
        model.learn(total_timesteps=total_timesteps)
        
        # Prueba del modelo: resetear y ejecutar acciones en el entorno
        obs = vec_env.reset()
        for _ in range(1000):
            action, _states = model.predict(obs, deterministic=True)
            obs, rewards, dones, infos = vec_env.step(action)
            # Renderizar el entorno original (si es que tiene implementado el método render)
            self.env.render()
