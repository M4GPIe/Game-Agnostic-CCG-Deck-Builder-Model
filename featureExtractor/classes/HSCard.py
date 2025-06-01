
from featureExtractor.classes.AbstractCard import AbstractCard
from typing import Dict
from featureExtractor.classes.KeywordProcessor import KeywordProcessor
from featureExtractor.classes.NLPProcessor import NLPProcessor
from featureExtractor.utils.helper_functions import is_numeric, parse_HS_card_name
from featureExtractor.utils.constants.HS_Constants import hearthstone_effect_references

class HSCard(AbstractCard):
  def __init__(self, card: Dict, keyword_processor: KeywordProcessor, nlp: NLPProcessor):
      """
          Parse a JSON object into card
      """

      power = card.get("attack",0)
      toughness = card.get("health",0)

      if not is_numeric(power) or not is_numeric(toughness):
          return None

      power = int(power)
      toughness = int(toughness)
      name = parse_HS_card_name(card.get("name", ""))
      card_type = card.get("type", "")
      totalManaCost = card.get("manaCost", 0)
      text = card.get("text", "")
      card_keywords = card.get("mechanics", [])

      # get keywords
      parsed_keywords = keyword_processor.extract_keywords(card_keywords=card_keywords, card_text = text)
      binary_keywords = [1 if k else 0 for k in parsed_keywords.values()]

      # get nlp features
      effects_object  = {}
      for effect in hearthstone_effect_references.keys():
          effects_object[effect]= False

      for effect, references in hearthstone_effect_references.items():

          for ref in references:
              found = nlp.text_query(base_text=text, query_text=ref)

              if found:
                  effects_object[effect]= True
                  break

      binary_effects = [1 if k else 0 for k in effects_object.values()]

      super().__init__(name, card_type, power, toughness, keywords=binary_keywords, effects=binary_effects, total_cost=totalManaCost)