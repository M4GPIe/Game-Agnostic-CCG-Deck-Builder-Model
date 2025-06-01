from typing import List, Dict

class KeywordProcessor:
    def __init__(self, keywords_list: List[str]):
        self.keywords_list = keywords_list

    def extract_keywords(self, card_text: str, card_keywords= None) -> Dict[str, bool]:
        """
            From keywords data object containing all searched keywords and card keywords array
            Return: dictionary from keywords to boolean
        """
        keywords = {}

        if card_keywords:
            for keyword in self.keywords_list:
                keywords[keyword] = keyword in card_keywords

        else:
            for keyword in self.keywords_list:
                keywords[keyword] = keyword in card_text

        return keywords
