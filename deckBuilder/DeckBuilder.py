import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random
from featureExtractor.classes.card import MTGCard
import json
import random

class DeckBuilderEnv(gym.Env):
    def __init__(self, n: int, k: int, history: bool, parsed_cards_file: str):
        super(DeckBuilderEnv, self).__init__()

        self.n = n  # deck size
        self.k = k  # random choice size
        self.history = history  # save current selected cards on state
        self.deck = [] 
        self.current_step = 0  
        self.parsed_cards_file = parsed_cards_file

        self.action_space = spaces.Discrete(k)

        if self.history:
            self.observation_space = spaces.Box(low=0, high=1, shape=(n + k, ), dtype=np.float32)
        else:
            self.observation_space = spaces.Box(low=0, high=1, shape=(k, ), dtype=np.float32)

        self.available_cards = self.generate_random_cards(parsed_cards_file)  

    def generate_random_cards(self, parsed_cards_file: str):
        
        with open(parsed_cards_file, 'r') as json_in:
            parsed_cards = json.load(json_in)

            random_cards = random.sample(parsed_cards, self.k)

            parsed_cards = []

            for card in random_cards:
                card = MTGCard(
                    name = card.get("name", ""),
                    card_type= card.get("card_type", ""),
                    mana_cost_by_color= card.get("mana_cost_by_color", 0),
                    convertedManaCost= card.get("convertedManaCost", {}),
                    power= card.get("power", 0),
                    toughness= card.get("toughness", 0),
                    card_effects= card.get("card_effects", {}),
                    card_keywords= card.get("card_keywords", {})
                )
                parsed_cards.append(card)
            return parsed_cards

    def step(self, action):
        selected_card = self.available_cards[action]

        self.deck.append(selected_card)

        self.current_step += 1

        if self.current_step >= self.n:
            victory_rate = self.simulate_deck(self.deck)
            reward = self.normalize_reward(victory_rate)
            done = True
        else:
            self.available_cards = self.generate_random_cards(self.parsed_cards_file)
            done = False
            reward = 0 

        state = self.get_state()

        return state, reward, done, {}

    def get_state(self):
        if not self.history:
            return np.array([card.to_vector() for card in self.available_cards])

        state = [card.to_vector() for card in self.deck] + [card.to_vector() for card in self.available_cards]
        return np.array(state)

    def simulate_deck(self, deck):
        victories = random.randint(0, 10)  
        return victories / 10  

    def normalize_reward(self, victory_rate):
        return 2 * victory_rate - 1  

    def reset(self):
        self.deck = []
        self.current_step = 0
        self.available_cards = self.generate_random_cards(self.parsed_cards_file)
        return self.get_state()

    def render(self):
        print(f"Deck: {self.deck}")
        print(f"Available Cards: {self.available_cards}")
        print(f"Step: {self.current_step}/{self.n}")