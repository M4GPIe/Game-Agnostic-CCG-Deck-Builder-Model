from utils.card import MTGCard
from typing import Dict

def is_numeric(value: str) -> bool:
    """
    Verifies if a value is numeric
    """
    try:
        int(value)  
        return True
    except ValueError:
        return False  
    
def get_forge_supported_cards()-> set[str]:
    # supported cards file
    input_file = 'content\supportedCards.txt' 

    names_set = set()

    with open(input_file, 'r', encoding='utf-8') as file:
        names_set = {line.strip() for line in file}

    #print(names_set)

    return names_set

def parse_card_data(card: Dict) -> MTGCard:
    """
        Transfors a MTGJson object to MTGCard class
    """

    # simulator supported cards
    names_set = get_forge_supported_cards()

    power = card.get("power", "0")
    toughness = card.get("toughness", "0")

    if not is_numeric(power) or not is_numeric(toughness):
        return None  

    name = card.get("name", "")
    card_type = card.get("type", "")
    mana_cost = card.get("manaCost", "")
    convertedManaCost = card.get("convertedManaCost", 0)
    power = int(card.get("power", 0)) if card.get("power") else 0
    toughness = int(card.get("toughness", 0)) if card.get("toughness") else 0
    text = card.get("text", "")
    card_keywords = card.get("keywords", [])

    print(name)
    if name not in names_set:
      print("NOT FOUND")
      return None

    print("FOUND")

    # create card instance
    mtg_card = MTGCard(
        name=name,
        card_type=card_type,
        mana_cost=mana_cost,
        convertedManaCost=convertedManaCost,
        power=power,
        toughness=toughness,
        text=text,
        card_keywords=card_keywords
    )

    return mtg_card