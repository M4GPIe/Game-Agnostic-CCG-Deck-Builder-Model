from abc import ABC, abstractmethod
from typing import Dict, List, Set, Literal

class AbstractCard(ABC):

  """
    Constructor:
      - name : Name of the card
      - card_type : Card type according to game rules e.g. creature, land
      - power : Attack points, damage dealt with basic attack
      - toughness : Card's life points
      - keywords : Ordered list with a bit for each keyword property the game has
      - effects : Ordered list with a bit for each effect parsed with the NLP analyzer
      - total_cost : Total mana cost
      - cost_by_color : List with a number for the cost of each mana color
  """
  def __init__(self, name: str, card_type: str, power: int, toughness: int, keywords: List[Literal[0,1]], effects: List[Literal[0,1]], total_cost: int, cost_by_color: List[int] = None):
    self.name = name
    self.card_type = card_type  # Card type according to game rules e.g. creature, land
    self.power = power  # Attack points, damage dealt with basic attack
    self.toughness = toughness  # Card's life points
    self.keywords = keywords  # Ordered list with a bit for each keyword property the game has
    self.effects = effects  # Ordered list with a bit for each effect parsed with the NLP analyzer
    self.total_cost = total_cost  # Total mana cost
    self.cost_by_color = cost_by_color # List with a number for the cost of each mana color

  def __str__(self) -> str:
      return (
          f"Card Name     : {self.name}\n"
          f"Card Type     : {self.card_type}\n"
          f"Power         : {self.power}\n"
          f"Toughness     : {self.toughness}\n"
          f"Total Cost    : {self.total_cost}\n"
          f"Cost by Color : {self.cost_by_color if self.cost_by_color else 'N/A'}\n"
          f"Keywords      : {''.join(map(str, self.keywords))}\n"
          f"Effects       : {''.join(map(str, self.effects))}"
      )