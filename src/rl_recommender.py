import gymnasium as gym
import numpy as np
import pandas as pd
from stable_baselines3 import DQN
from stable_baselines3.common.env_checker import check_env
import pickle

class RecommendationEnv(gym.Env):
    def __init__(self, data_csv="data/processed_images.csv", embeddings_file="models/embeddings/embeddings.pkl"):
        super().__init__()
        self.data = pd.read_csv(data_csv)
        with open(embeddings_file, "rb") as f:
            self.embeddings = pickle.load(f)

        self.action_space = gym.spaces.Discrete(len(self.data))
        self.observation_space = gym.spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(self.embeddings.shape[1],),
            dtype=np.float32
        )
        self.current_state = None
        self.target_product = None

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.target_product = np.random.choice(len(self.data))
        self.current_state = self.embeddings[self.target_product]
        return self.current_state, {}

    def step(self, action):
        reward = 1.0 if action == self.target_product else -0.1
        self.current_state = self.embeddings[action]
        terminated = True  
        truncated = False  
        info = {}
        return self.current_state, reward, terminated, truncated, info

    def render(self):
        pass

def train_recommender():
    env = RecommendationEnv()
    check_env(env)
    model = DQN("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=10000)
    model.save("models/dqn_model/dqn_recommender")
    print("✅ DQN model saved")

def recommend_products(model_path, state):
    model = DQN.load(model_path)
    action, _ = model.predict(state)
    return action

if __name__ == "__main__":
    train_recommender()
