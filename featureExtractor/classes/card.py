# DEFINITION OF CARD OBJECT

from typing import List, Dict
import re

class MTGCard:
    def __init__(self, name: str, card_type: str, mana_cost: str, convertedManaCost: int, power: int, toughness: int, card_effects: Dict[str, bool], card_keywords: List[str]):
        self.name = name  
        self.card_type = card_type  
        self.power = power  
        self.toughness = toughness  
        self.keywords = card_keywords
        self.effects = card_effects
        self.convertedManaCost = convertedManaCost 
        self.mana_cost_by_color = self.parse_mana_cost(mana_cost)

    def parse_mana_cost(self, mana_cost: str) -> Dict[str, int]:
        """
            From card's mana cost return a dictionary with cost by color in standar format
        """
        
        # black, blue, red, green, white and colorless
        color_symbols = {'B': 0, 'U': 0, 'R': 0, 'G': 0, 'W': 0, 'C': 0}  

        # mana is expresed in string form like "{2}{B}{G}" meaning 2 colorless, one black and one green
        mana_pattern = r'\{(\d+)\}|\{(B|U|R|G|W|C)\}'  

        matches = re.findall(mana_pattern, mana_cost)

        for match in matches:
            if match[0]:  # if matches the first part is a number represeting colorless
                color_symbols['C'] += int(match[0]) 
            elif match[1]:  #if matches a letter
                color_symbols[match[1]] += 1 

        return color_symbols

    def __repr__(self):
        return (f"MTGCard(name={self.name}, "
                f"card_type={self.card_type}, "
                f"mana_cost={self.mana_cost_by_color}, "
                f"convertedManaCost={self.convertedManaCost}, "
                f"power={self.power}, "
                f"toughness={self.toughness}, "
                f"keywords={self.keywords}, "
                f"effects={self.effects})")