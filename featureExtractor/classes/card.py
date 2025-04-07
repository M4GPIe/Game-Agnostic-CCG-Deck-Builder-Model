# DEFINITION OF CARD OBJECT

from typing import List, Dict
import numpy as np

class MTGCard:
    def __init__(self, name: str, card_type: str, mana_cost_by_color: Dict[str, int], convertedManaCost: int, power: int, toughness: int, card_effects: Dict[str, bool], card_keywords: Dict[str, bool]):
        self.name = name  
        self.card_type = card_type  
        self.power = power  
        self.toughness = toughness  
        self.keywords = card_keywords
        self.effects = card_effects
        self.convertedManaCost = convertedManaCost 
        self.mana_cost_by_color = mana_cost_by_color

    def __repr__(self):
        return (f"MTGCard(name={self.name}, "
                f"card_type={self.card_type}, "
                f"mana_cost={self.mana_cost_by_color}, "
                f"convertedManaCost={self.convertedManaCost}, "
                f"power={self.power}, "
                f"toughness={self.toughness}, "
                f"keywords={self.keywords}, "
                f"effects={self.effects})")
    
    def to_vector(self):
        # Convierte las características de la carta en un vector que pueda ser utilizado por el modelo
        # Aquí se extraen las características principales de la carta (se pueden ajustar o agregar más)
        keyword_vector = [1 if k else 0 for k in self.keywords.values()]  # Ejemplo de palabras clave
        effect_vector = [1 if k else 0 for k in self.effects.values()]  # Efectos comunes
        mana_vector = list(self.mana_cost_by_color.values())  # Desglosado por colores
        power_toughness_vector = [self.power if self.power is not None else 0, self.toughness if self.toughness is not None else 0]
        return np.array(mana_vector + power_toughness_vector + keyword_vector + effect_vector)