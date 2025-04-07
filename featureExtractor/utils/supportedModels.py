from enum import Enum

class SupportedModels(Enum):
    ALL_MINILM_L6_V2 = "sentence-transformers/all-MiniLM-L6-v2"
    ALL_MPNET_BASE_V2 = "sentence-transformers/all-mpnet-base-v2"
    PARAPHRASE_DISTILROBERTA_BASE_V1 = "sentence-transformers/paraphrase-distilroberta-base-v1"
    DISTILBERT_BASE_NLI_STSB_MEAN_TOKENS = "sentence-transformers/distilbert-base-nli-stsb-mean-tokens"