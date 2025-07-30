# char/augmentor.py

import random
import string
from typing import List, Optional

from nlp_augmentation.utils.resources import load_qwerty_map

_DEFAULT_ALPHABET = string.ascii_letters + string.digits + string.punctuation


class CharAugmentor:
    """
    Символьный аугментатор: удаление, вставка, подмена символов и др.
    """

    def __init__(self, seed: Optional[int] = None) -> None:
        self._rng = random.Random(seed)
        self._neighbor_map = load_qwerty_map()

    @staticmethod
    def _check_p(p: float) -> None:
        if not 0.0 <= p <= 1.0:
            raise ValueError("p must be in [0, 1]")

    def delete(self, text: str, p: float = 0.005) -> str:
        self._check_p(p)
        rnd = self._rng.random
        return "".join(ch for ch in text if rnd() > p)

    def insert(self, text: str, p: float = 0.005, alphabet: Optional[str] = None) -> str:
        self._check_p(p)
        alpha = alphabet or _DEFAULT_ALPHABET
        rnd, choice = self._rng.random, self._rng.choice
        out: List[str] = []
        for ch in text:
            if rnd() < p:
                out.append(choice(alpha))
            out.append(ch)
            if rnd() < p:
                out.append(choice(alpha))
        return "".join(out)

    def substitute(self, text: str, p: float = 0.05) -> str:
        self._check_p(p)
        out: List[str] = []
        for ch in text:
            if self._rng.random() < p:
                src = self._neighbor_map.get(ch.lower(), _DEFAULT_ALPHABET)
                out.append(self._rng.choice(src))
            else:
                out.append(ch)
        return "".join(out)

    def swap(self, text: str, p: float = 0.005) -> str:
        self._check_p(p)
        chars = list(text)
        rnd = self._rng.random
        i = 0
        while i < len(chars) - 1:
            if rnd() < p:
                chars[i], chars[i + 1] = chars[i + 1], chars[i]
                i += 2
            else:
                i += 1
        return "".join(chars)

    def case(self, text: str, p: float = 0.005) -> str:
        self._check_p(p)
        rnd = self._rng.random
        return "".join(ch.swapcase() if rnd() < p else ch for ch in text)
