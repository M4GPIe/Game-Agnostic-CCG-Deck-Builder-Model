# DEFINITION OF CARD OBJECT

from typing import List, Dict
import re
from sentence_transformers import SentenceTransformer, util

from utils.keywords import keywords_data
from utils.effects import effect_references, initial_effects_object

# NLP language model
transformer = SentenceTransformer("all-MiniLM-L6-v2")

class MTGCard:
    def __init__(self, name: str, card_type: str, mana_cost: str, convertedManaCost: int, power: int, toughness: int, text: str, card_keywords: List[str]):
        self.name = name  
        self.card_type = card_type  
        self.power = power  
        self.toughness = toughness  
        self.keywords = self.extract_keywords(keywords_data , card_keywords)  
        self.effects = self.extract_effects(text)  
        self.convertedManaCost = convertedManaCost 
        self.mana_cost_by_color = self.parse_mana_cost(mana_cost)

    def extract_keywords(self, keywords_data: Dict , card_keywords: List[str]) -> Dict[str, bool]:
        """
            From keywords data object containing all searched keywords and card keywords array
            Return: dictionary from keywords to boolean 
        """
        keywords = {}

        #ignore keyword agrupations
        for _, keyword_list in keywords_data.items():
            for keyword in keyword_list:
                keywords[keyword] = keyword in card_keywords

        return keywords


    def extract_effects(self, text: str) -> Dict[str, bool]:
        """
            From effects refferences and NLP model extract all effects present in card's text
        """

        effects = initial_effects_object

        threshold = 0.6 #minimum similarity

        #print(f"Procesando el texto: {text}")

        # Divide text in chunks by phrase
        chunks = re.split(r'(?<=[.!?])\s+', text)

        # For every effect and chunk loop all refs of the effect searching max similarity
        for effect, refs in effect_references.items():
            max_similarity = 0.0

            for chunk in chunks:
                if not chunk.strip():
                    continue    #avoid empty chunks

                embedding_chunk = transformer.encode(chunk, convert_to_tensor=True)

                for ref in refs:
                    embedding_ref = transformer.encode(ref, convert_to_tensor=True)
                    similarity = util.cos_sim(embedding_chunk, embedding_ref).item()

                    if similarity > max_similarity:
                        max_similarity = similarity

            #print(f"Máxima similitud para '{effect}': {max_similarity}")

            if max_similarity > threshold:
                effects[effect] = True

        return effects

    def parse_mana_cost(self, mana_cost: str) -> Dict[str, int]:
        """
            From card's mana cost retur a dictionary with cost by color in standar format
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