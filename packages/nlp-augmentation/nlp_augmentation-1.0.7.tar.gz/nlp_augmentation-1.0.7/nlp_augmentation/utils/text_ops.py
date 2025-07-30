# utils/text_ops.py

import re
from typing import List

import spacy
import functools

@functools.lru_cache(maxsize=1)
def _get_nlp():
    return spacy.load("en_core_web_sm", exclude=["parser", "ner", "lemmatizer"])

_PUNCT_FIX = re.compile(r"\s([?.!,;:'’])")

def tokenize(text: str) -> List[str]:
    return [tok.text for tok in _get_nlp()(text)]

def detokenize(tokens: List[str]) -> str:
    return _PUNCT_FIX.sub(r"\1", " ".join(tokens))
