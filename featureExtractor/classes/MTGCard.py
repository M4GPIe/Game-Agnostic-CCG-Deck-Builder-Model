import re
from featureExtractor.classes.AbstractCard import AbstractCard
from typing import Dict
from featureExtractor.classes.KeywordProcessor import KeywordProcessor
from featureExtractor.classes.NLPProcessor import NLPProcessor
from featureExtractor.utils.helper_functions import is_numeric
from featureExtractor.utils.constants.MTG_Constants import MTG_effect_references
from typing import List, Literal

class MTGCard(AbstractCard):
  def __init__(self, card: Dict, keyword_processor: KeywordProcessor, nlp: NLPProcessor):
      """
          Parse a JSON object into card
      """

      power = card.get("power",0)
      toughness = card.get("toughness",0)

      if not is_numeric(power) or not is_numeric(toughness):
          return None

      power = int(power)
      toughness = int(toughness)
      name = card.get("name", "")
      card_type = card.get("type", "")
      mana_cost = card.get("manaCost", "")
      convertedManaCost = card.get("convertedManaCost", 0)
      text = card.get("text", "")
      card_keywords = card.get("keywords", [])

      # get keywords
      parsed_keywords = keyword_processor.extract_keywords(card_keywords=card_keywords, card_text = text)
      binary_keywords = [1 if k else 0 for k in parsed_keywords.values()]

      # get nlp features
      effects_object  = {}
      for effect in MTG_effect_references.keys():
          effects_object[effect]= False

      for effect, references in MTG_effect_references.items():

          for ref in references:
              found = nlp.text_query(base_text=text, query_text=ref)

              if found:
                  effects_object[effect]= True
                  break

      binary_effects = [1 if k else 0 for k in effects_object.values()]

      # parse mana colors
      # black, blue, red, green, white and colorless
      mana_cost_by_color = {'B': 0, 'U': 0, 'R': 0, 'G': 0, 'W': 0, 'C': 0}

      # mana is expresed in string form like "{2}{B}{G}" meaning 2 colorless, one black and one green
      mana_pattern = r'\{(\d+)\}|\{(B|U|R|G|W|C)\}'

      matches = re.findall(mana_pattern, mana_cost)

      for match in matches:
          if match[0]:  # if matches the first part is a number represeting colorless
              mana_cost_by_color['C'] += int(match[0])
          elif match[1]:  #if matches a letter
              mana_cost_by_color[match[1]] += 1

      super().__init__(name, card_type, power, toughness, keywords=binary_keywords, effects=binary_effects, total_cost=convertedManaCost, cost_by_color=mana_cost_by_color)

  def __init__(self, name: str, card_type: str, power: int, toughness: int, keywords: List[Literal[0,1]], effects: List[Literal[0,1]], total_cost: int, cost_by_color: List[int] = None):
        """
        Initializes the card directly with parsed parameters, including pre-parsed binary keywords and effects
        """
        # No need to parse keywords and effects as they are already passed as binary lists
        super().__init__(name, card_type, power, toughness, keywords=keywords, effects=effects, total_cost=total_cost, cost_by_color=cost_by_color)