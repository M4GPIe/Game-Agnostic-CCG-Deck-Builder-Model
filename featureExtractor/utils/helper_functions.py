import re
import string

def is_numeric(value: str) -> bool:
    """
    Verifies if a value is numeric
    """
    try:
        int(value)  
        return True
    except (ValueError, TypeError):
        return False  

def parse_HS_card_name(name: str)->str:
    """
    Format to HS simulator standard
    - No white spaces or apostrophes or any punctuation
    - Camelcase with first Upper
    """
    # Elimina todos los signos de puntuación
    name_clean = re.sub(rf"[{re.escape(string.punctuation)}]", "", name)

    # Convierte a CamelCase
    formatted_name = ''.join(word.capitalize() for word in name_clean.split())

    return formatted_name